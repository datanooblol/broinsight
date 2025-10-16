from pydantic import BaseModel
from typing import List, Any, Optional

class TableSpec(BaseModel):
    rows: int
    columns: int
    duplicates: int
    evidences: dict

class FieldDescription(BaseModel):
    field_name:str
    description:str

class FieldDescriptions(BaseModel):
    descriptions:List[FieldDescription]

class QualityIssue(BaseModel):
    type: str
    severity: str  # critical, moderate, minor
    description: str

class FieldQualityAssessment(BaseModel):
    field_name: str
    quality: str  # poor, fair, good
    issues: List[QualityIssue] = []
    issue_count: int = 0

class DataQualityAssessment(BaseModel):
    field_assessments: List[FieldQualityAssessment] = []
    overall_quality: Optional[str] = None  # poor, fair, good
    total_issues: int = 0
    # assessment_summary: Optional[str] = None  # LLM-generated summary

class FieldSpec(BaseModel):
    field_name: str
    data_type: str
    missing_values: int
    missing_values_pct: float
    unique_values: int
    unique_values_pct: float
    most_frequent: dict
    statistics: dict
    description: Optional[str] = None

class Metadata(BaseModel):
    table_name: str
    table_description: str
    table_spec: TableSpec
    field_spec: List[FieldSpec]
    field_descriptions: Optional[FieldDescriptions] = None
    data_quality: Optional[DataQualityAssessment] = None
    
    def add_field_descriptions(self, field_descriptions: FieldDescriptions):
        """Add descriptions to fields after initialization"""
        self.field_descriptions = field_descriptions
        desc_dict = {fd.field_name: fd.description for fd in field_descriptions.descriptions}
        for field in self.field_spec:
            if field.field_name in desc_dict:
                field.description = desc_dict[field.field_name]
    
    def add_data_quality_assessment(self, assessment: DataQualityAssessment):
        """Add data quality assessment to metadata"""
        self.data_quality = assessment

def create_field_specs_from_profile(field_profile: dict, field_descriptions: Optional[FieldDescriptions] = None) -> List[FieldSpec]:
    """Convert raw field profile to FieldSpec objects"""
    field_specs = []
    
    desc_dict = {}
    if field_descriptions:
        desc_dict = {fd.field_name: fd.description for fd in field_descriptions.descriptions}
    
    for field_name, profile in field_profile.items():
        description = desc_dict.get(field_name)
        field_spec = FieldSpec(
            field_name=field_name,
            data_type=profile['data_type'],
            missing_values=profile['missing_values'],
            missing_values_pct=profile['missing_values_pct'],
            unique_values=profile['unique_values'],
            unique_values_pct=profile['unique_values_pct'],
            most_frequent=profile['most_frequent'],
            statistics=profile.get('statistics'),
            description=description
        )
        field_specs.append(field_spec)
    
    return field_specs

def create_data_quality_assessment(field_profile: dict) -> DataQualityAssessment:
    """Create DataQualityAssessment from field profile using existing criteria"""
    from broinsight.data_quality.criteria import assess_data_quality
    
    # Use existing assessment logic
    quality_results = assess_data_quality(field_profile)
    
    field_assessments = []
    total_issues = 0
    quality_levels = []
    
    for field_name, result in quality_results.items():
        summary = result['summary']
        
        # Convert issues to QualityIssue objects
        issues = [QualityIssue(**issue) for issue in summary['issues']]
        
        field_assessment = FieldQualityAssessment(
            field_name=field_name,
            quality=summary['quality'],
            issues=issues,
            issue_count=summary['issue_count']
        )
        
        field_assessments.append(field_assessment)
        total_issues += summary['issue_count']
        quality_levels.append(summary['quality'])
    
    # Determine overall quality
    if 'poor' in quality_levels:
        overall_quality = 'poor'
    elif 'fair' in quality_levels:
        overall_quality = 'fair'
    else:
        overall_quality = 'good'
    
    return DataQualityAssessment(
        field_assessments=field_assessments,
        overall_quality=overall_quality,
        total_issues=total_issues
    )