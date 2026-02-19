from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Dashboard Response
class DashboardMetrics(BaseModel):
    role: str
    metrics: Dict[str, Any]

# Asset Reports
class AssetByStatusReport(BaseModel):
    status: str
    count: int
    total_value: float

class AssetByLocationReport(BaseModel):
    location_id: str
    location_name: str
    count: int

class AssetByCategoryReport(BaseModel):
    category_id: str
    category_name: str
    count: int
    total_value: float

class AssetByCustodianReport(BaseModel):
    custodian_id: Optional[str]
    custodian_name: str
    count: int

class AssetLifecycleReport(BaseModel):
    asset_id: str
    asset_name: str
    acquisition_date: date
    age_years: float
    useful_life_years: int
    remaining_life_years: float
    depreciation_percentage: float

# Verification Reports
class VerificationCoverageReport(BaseModel):
    total_assets: int
    verified_count: int
    coverage_percentage: float
    period_start: Optional[date]
    period_end: Optional[date]

class VerificationSessionSummary(BaseModel):
    session_id: str
    session_name: str
    session_type: str
    status: str
    target_count: int
    verified_count: int
    completion_percentage: float

# Operations Reports
class TransferSummaryReport(BaseModel):
    total_transfers: int
    pending_count: int
    approved_count: int
    rejected_count: int
    period_start: Optional[date]
    period_end: Optional[date]

class DisposalSummaryReport(BaseModel):
    total_disposals: int
    pending_count: int
    approved_count: int
    rejected_count: int
    by_type: Dict[str, int]

# Financial Reports
class TotalValueReport(BaseModel):
    total_value: float
    currency: str = "USD"
    asset_count: int
    by_category: List[Dict[str, Any]]

class DepreciationReport(BaseModel):
    asset_id: str
    asset_name: str
    acquisition_cost: float
    acquisition_date: date
    useful_life_years: int
    age_years: float
    accumulated_depreciation: float
    current_value: float
    depreciation_percentage: float

class AcquisitionTrendReport(BaseModel):
    period: str  # "2024-Q1", "2024-01", etc
    count: int
    total_value: float

# Maintenance Reports
class MaintenanceDueReport(BaseModel):
    asset_id: str
    asset_name: str
    last_maintenance_date: Optional[date]
    days_since_maintenance: Optional[int]
    recommended_interval_days: int = 180  # 6 months default

class MaintenanceHistoryReport(BaseModel):
    asset_id: str
    asset_name: str
    maintenance_count: int
    total_cost: float
    last_maintenance_date: Optional[date]
