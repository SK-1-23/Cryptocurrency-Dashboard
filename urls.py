from django.conf.urls import patterns, url
from final_year import views

urlpatterns = patterns('',
	url(r'^signup/',views.signup_view , name = 'signup'),
	url(r'^register/',views.register_view , name = 'register'),
	url(r'^signin',views.login_view,name = 'sign in'),
	url(r'^logout',views.logout,name = 'Logout'),
	url(r'^authenticate',views.authenticate_view,name='authenticate'),
	url(r'^dashboard',views.render_dashboard,name='render_dashboard'),
	url(r'^save_custom_alert',views.save_custom_alert,name='save_custom_alert'),
	url(r'^render_profile_content',views.render_profile_content,name='render_profile_content'),
	url(r'^save_user_profile',views.save_user_profile,name='save_user_profile'),
	url(r'^render_faq_content',views.render_faq_content,name='render_faq_content'),
)
