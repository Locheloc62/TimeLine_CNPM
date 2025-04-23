from flask import redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import Category, Product, UserEnum
from BookStore import app, db,dao
from flask_login import logout_user, current_user


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN


class MyCategoryView(AuthenticatedView):
    column_list = ['id', 'name', 'products']
    column_filters = ['name']
    column_searchable_list = ['name']
    can_export = True

class MyProductView(AuthenticatedView):
    column_list = ['id', 'name', 'price', 'cate_id']
    column_filters = ['name']
    column_searchable_list = ['name']
    can_export = True


class LogoutAdmin(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('/admin/stats.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = dao.count_product_by_cate()
        return self.render('admin/index.html', stats=stats)

admin = Admin(app=app, name="BOOKSTORE WEBSITE", template_mode="bootstrap4", index_view=MyAdminIndexView())

admin.add_view(MyCategoryView(Category, db.session))
admin.add_view(MyProductView(Product, db.session))

admin.add_view(StatsView(name="Thống kê"))
admin.add_view(LogoutAdmin(name="Đăng xuất"))