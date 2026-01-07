from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from app.models.asset import Asset
from app.models.operations import Transfer, Disposal, Maintenance
from app.models.verification import VerificationSession, AssetVerification
from app.models.master_data import Location, AssetCategory
from app.models.user import User
from app.schemas.reports import *

class ReportService:
    
    # === DASHBOARD ===
    @staticmethod
    def get_dashboard_metrics(session: Session, roles: List[str]) -> Dict[str, Any]:
        """Role-specific dashboard metrics"""
        metrics = {}
        
        # Check privileges based on presence of roles in the list
        is_scm = any("Supply Chain Manager" in r for r in roles) if roles else False
        is_admin = any("IT Admin" in r for r in roles) if roles else False
        
        # Simple check: If exact match logic is preferred:
        # is_scm = "Supply Chain Manager" in roles
        # is_admin = "IT Admin" in roles
        # Use loose check to handle potential string variations if needed, but strict list check is safer if Enum used consistently.
        # Given "Array(4) ['IT Admin', ...]" log, strict check is likely fine, but let's be robust.
        
        has_manager_access = is_scm or is_admin
        
        if has_manager_access:
            # Total assets
            total_assets = session.exec(select(func.count(Asset.scom_asset_id))).one()
            metrics["total_assets"] = total_assets
            
            # Assets by status
            pending_transfers = session.exec(select(func.count(Transfer.transfer_id)).where(Transfer.status == "PENDING")).one()
            metrics["pending_transfers"] = pending_transfers
            
            # Recent verifications
            today = date.today()
            week_ago = today - timedelta(days=7)
            recent_verifications = session.exec(
                select(func.count(AssetVerification.verification_id))
                .where(AssetVerification.verified_at >= week_ago)
            ).one()
            metrics["verifications_last_week"] = recent_verifications
            
        if is_admin:
            # Maintenance due
            maintenance_count = session.exec(select(func.count(Maintenance.maintenance_id))).one()
            metrics["total_maintenance_records"] = maintenance_count
            
        return metrics
    
    # === ASSET REPORTS ===
    @staticmethod
    def get_assets_by_status(session: Session) -> List[AssetByStatusReport]:
        """Asset count and value by status"""
        query = select(
            Asset.asset_status,
            func.count(Asset.scom_asset_id).label("count"),
            func.sum(Asset.acquisition_price).label("total_value")
        ).group_by(Asset.asset_status)
        
        results = session.exec(query).all()
        
        return [
            AssetByStatusReport(
                status=str(row[0]),
                count=row[1],
                total_value=float(row[2] or 0)
            )
            for row in results
        ]
    
    @staticmethod
    def get_assets_by_location(session: Session) -> List[AssetByLocationReport]:
        """Asset count per location"""
        query = select(
            Location.location_id,
            Location.location_name,
            func.count(Asset.scom_asset_id).label("count")
        ).join(Asset, Asset.location_id == Location.location_id, isouter=True
        ).group_by(Location.location_id, Location.location_name)
        
        results = session.exec(query).all()
        
        return [
            AssetByLocationReport(
                location_id=row[0],
                location_name=row[1],
                count=row[2] or 0
            )
            for row in results
        ]
    
    @staticmethod
    def get_assets_by_custodian(session: Session, limit: int = 10) -> List[AssetByCustodianReport]:
        """Top asset holders"""
        query = select(
            Asset.custodian_id,
            User.full_name,
            func.count(Asset.scom_asset_id).label("count")
        ).join(User, Asset.custodian_id == User.user_id, isouter=True
        ).group_by(Asset.custodian_id, User.full_name
        ).order_by(func.count(Asset.scom_asset_id).desc()
        ).limit(limit)
        
        results = session.exec(query).all()
        
        return [
            AssetByCustodianReport(
                custodian_id=row[0],
                custodian_name=row[1] or "Unassigned",
                count=row[2]
            )
            for row in results
        ]
    
    # === VERIFICATION REPORTS ===
    @staticmethod
    def get_verification_coverage(
        session: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> VerificationCoverageReport:
        """Percentage of assets verified in period"""
        total_assets = session.exec(select(func.count(Asset.scom_asset_id))).one()
        
        query = select(func.count(func.distinct(AssetVerification.asset_id)))
        
        if start_date:
            query = query.where(AssetVerification.scanned_at >= start_date)
        if end_date:
            query = query.where(AssetVerification.scanned_at <= end_date)
        
        verified_count = session.exec(query).one()
        
        coverage = (verified_count / total_assets * 100) if total_assets > 0 else 0
        
        return VerificationCoverageReport(
            total_assets=total_assets,
            verified_count=verified_count,
            coverage_percentage=round(coverage, 2),
            period_start=start_date,
            period_end=end_date
        )
    
    # === OPERATIONS REPORTS ===
    @staticmethod
    def get_transfer_summary(
        session: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransferSummaryReport:
        """Transfer statistics"""
        query = select(Transfer)
        
        if start_date:
            query = query.where(Transfer.requested_at >= start_date)
        if end_date:
            query = query.where(Transfer.requested_at <= end_date)
        
        transfers = session.exec(query).all()
        
        pending = sum(1 for t in transfers if t.status == "PENDING")
        approved = sum(1 for t in transfers if t.status == "APPROVED")
        rejected = sum(1 for t in transfers if t.status == "REJECTED")
        
        return TransferSummaryReport(
            total_transfers=len(transfers),
            pending_count=pending,
            approved_count=approved,
            rejected_count=rejected,
            period_start=start_date,
            period_end=end_date
        )
    
    # === FINANCIAL REPORTS ===
    @staticmethod
    def get_total_value(session: Session) -> TotalValueReport:
        """Total asset value"""
        total = session.exec(select(func.sum(Asset.acquisition_price))).one() or 0
        count = session.exec(select(func.count(Asset.scom_asset_id))).one()
        
        # By category
        by_cat_query = select(
            AssetCategory.name,
            func.sum(Asset.acquisition_price).label("value")
        ).join(Asset, Asset.sub_category_id == AssetCategory.category_id, isouter=True
        ).group_by(AssetCategory.name)
        
        by_category = [
            {"category": row[0], "value": float(row[1] or 0)}
            for row in session.exec(by_cat_query).all()
        ]
        
        return TotalValueReport(
            total_value=float(total),
            asset_count=count,
            by_category=by_category
        )
    
    # === MAINTENANCE REPORTS ===
    @staticmethod
    def get_maintenance_due(session: Session, days_threshold: int = 180) -> List[MaintenanceDueReport]:
        """Assets needing maintenance"""
        # Get latest maintenance date per asset
        subq = select(
            Maintenance.asset_id,
            func.max(Maintenance.date_of_maintenance).label("last_date")
        ).group_by(Maintenance.asset_id).subquery()
        
        # Assets with last maintenance beyond threshold
        query = select(Asset, subq.c.last_date).join(
            subq, Asset.scom_asset_id == subq.c.asset_id, isouter=True
        )
        
        results = []
        today = date.today()
        
        for asset, last_maint in session.exec(query).all():
            if last_maint:
                days_since = (today - last_maint).days
                if days_since >= days_threshold:
                    results.append(MaintenanceDueReport(
                        asset_id=asset.scom_asset_id,
                        asset_name=asset.asset_name,
                        last_maintenance_date=last_maint,
                        days_since_maintenance=days_since,
                        recommended_interval_days=days_threshold
                    ))
            else:
                # Never maintained
                results.append(MaintenanceDueReport(
                    asset_id=asset.scom_asset_id,
                    asset_name=asset.asset_name,
                    last_maintenance_date=None,
                    days_since_maintenance=None,
                    recommended_interval_days=days_threshold
                ))
        
        return results[:50]  # Limit to 50 for performance
