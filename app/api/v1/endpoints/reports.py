from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep, CurrentUser
from app.services.report_service import ReportService
from app.schemas.reports import *

router = APIRouter()

@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Role-specific dashboard metrics for current user.
    """
    metrics = ReportService.get_dashboard_metrics(session, current_user.role)
    return DashboardMetrics(role=current_user.role, metrics=metrics)

# === ASSET REPORTS ===

@router.get("/assets/by-status", response_model=List[AssetByStatusReport])
def get_assets_by_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Asset distribution by status with counts and total values.
    """
    return ReportService.get_assets_by_status(session)

@router.get("/assets/by-location", response_model=List[AssetByLocationReport])
def get_assets_by_location(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Asset count per location.
    """
    return ReportService.get_assets_by_location(session)

@router.get("/assets/by-custodian", response_model=List[AssetByCustodianReport])
def get_assets_by_custodian(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(10, description="Number of top custodians to return"),
) -> Any:
    """
    Top asset holders/custodians.
    """
    return ReportService.get_assets_by_custodian(session, limit)

# === VERIFICATION REPORTS ===

@router.get("/verifications/coverage", response_model=VerificationCoverageReport)
def get_verification_coverage(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
) -> Any:
    """
    Verification coverage percentage - % of assets scanned in date range.
    """
    return ReportService.get_verification_coverage(session, start_date, end_date)

# === OPERATIONS REPORTS ===

@router.get("/transfers/summary", response_model=TransferSummaryReport)
def get_transfer_summary(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
) -> Any:
    """
    Transfer statistics: total, pending, approved, rejected counts.
    """
    return ReportService.get_transfer_summary(session, start_date, end_date)

# === FINANCIAL REPORTS ===

@router.get("/financial/total-value", response_model=TotalValueReport)
def get_total_value(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Total asset value across all assets with breakdown by category.
    """
    return ReportService.get_total_value(session)

# === MAINTENANCE REPORTS ===

@router.get("/maintenance/due", response_model=List[MaintenanceDueReport])
def get_maintenance_due(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    days_threshold: int = Query(180, description="Days since last maintenance to flag as due"),
) -> Any:
    """
    Assets needing maintenance (overdue or never maintained).
    """
    return ReportService.get_maintenance_due(session, days_threshold)
