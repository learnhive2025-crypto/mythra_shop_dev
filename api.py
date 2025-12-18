from fastapi import APIRouter

from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.staff_routes import router as staff_router
from routes.category_routes import router as category_router
from routes.Product import router as product_router
from routes.purchase_routes import router as purchase_router
from routes.sales_routes import router as sales_router
from routes.stock_routes import router as stock_router
from routes.report_routes import router as report_router
from routes.dashboard_routes import router as dashboard_router
from routes.profit_routes import router as profit_router
from routes.analytics_routes import router as analytics_router
from routes.export_routes import router as export_router
from routes.excel_routes import router as excel_router
from routes.purchase_analytics import router as purchase_analytics_router
api_router = APIRouter()


api_router.include_router(purchase_analytics_router)
api_router.include_router(excel_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(staff_router)
api_router.include_router(category_router)
api_router.include_router(product_router)
api_router.include_router(purchase_router)
api_router.include_router(sales_router)
api_router.include_router(stock_router)
api_router.include_router(report_router)
api_router.include_router(dashboard_router)
api_router.include_router(profit_router)
api_router.include_router(analytics_router)
api_router.include_router(export_router)