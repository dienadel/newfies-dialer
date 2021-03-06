from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import *
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.db.models import Q
from notification import models as notification
from dialer_campaign.models import common_contact_authorization
from dialer_campaign.views import current_view, notice_count
from dialer_campaign.function_def import user_dialer_setting_msg, variable_value
from dialer_settings.models import DialerSetting
from user_profile.models import UserProfile
from user_profile.forms import *


@login_required
def customer_detail_change(request):
    """User Detail change on Customer UI

    **Attributes**:

        * ``form`` - UserChangeDetailForm, PasswordChangeForm, CheckPhoneNumberForm
        * ``template`` - 'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_detail = User.objects.get(username=request.user)
    user_detail_form = UserChangeDetailForm(user=request.user,
                                            instance=user_detail)
    user_password_form = PasswordChangeForm(user=request.user)
    check_phone_no_form = CheckPhoneNumberForm()

    try:
        user_ds = UserProfile.objects.get(user=request.user)
        dialer_set = DialerSetting.objects.get(id=user_ds.dialersetting.id)
    except:
        dialer_set = ''

    user_notification = \
    notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    msg_detail = ''
    msg_pass = ''
    msg_number = ''
    msg_note = ''
    error_detail = ''
    error_pass = ''
    error_number = ''
    selected = 0

    if 'selected' in request.GET:
        selected = request.GET['selected']

    if request.GET.get('msg_note') == 'true':
        msg_note = request.session['msg_note']
        
    if request.method == 'POST':
        if request.POST['form-type'] == "change-detail":
            user_detail_form = UserChangeDetailForm(request.user, request.POST,
                                                    instance=user_detail)
            selected = 0
            if user_detail_form.is_valid():
                user_detail_form.save()
                msg_detail = _('Your detail has been changed successfully.')
            else:
                error_detail = _('Please correct the errors below.')
        elif request.POST['form-type'] == "check-number": # check phone no
            selected = 4
            check_phone_no_form = CheckPhoneNumberForm(data=request.POST)
            if not common_contact_authorization(request.user,
                                                request.POST['phone_number']):
                error_number = _('This phone number is not authorized.')
            else:
                msg_number = _('This phone number is authorized.')
        else: # "change-password"
            user_password_form = PasswordChangeForm(user=request.user,
                                                    data=request.POST)
            selected = 1
            if user_password_form.is_valid():
                user_password_form.save()
                msg_pass = _('Your password has been changed successfully.')
            else:
                error_pass = _('Please correct the errors below.')

    template = 'frontend/registration/user_detail_change.html'
    data = {
        'module': current_view(request),
        'user_detail_form': user_detail_form,
        'user_password_form': user_password_form,
        'check_phone_no_form': check_phone_no_form,
        'user_notification': user_notification,
        'msg_detail': msg_detail,
        'msg_pass': msg_pass,
        'msg_number': msg_number,
        'msg_note': msg_note,
        'selected': selected,
        'error_detail': error_detail,
        'error_pass': error_pass,
        'error_number': error_number,
        'notice_count': notice_count(request),
        'dialer_set': dialer_set,
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))

def call_style(val):
    unseen_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/new.png);"'
    seen_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/tick.png);"'
    if val == 1:
        return unseen_style
    else:
        return seen_style

# Notification
@login_required
def notification_grid(request):
    """notification list in json format for flexigrid

    **Model**: notification.Notice
    """
    page = variable_value(request, 'page')
    rp = variable_value(request, 'rp')
    sortname = variable_value(request, 'sortname')
    sortorder = variable_value(request, 'sortorder')
    query = variable_value(request, 'query')
    qtype = variable_value(request, 'qtype')

    # page index
    if int(page) > 1:
        start_page = (int(page) - 1) * int(rp)
        end_page = start_page + int(rp)
    else:
        start_page = int(0)
        end_page = int(rp)


    #notification_list = []
    sortorder_sign = ''
    if sortorder == 'desc':
        sortorder_sign = '-'

    user_notification = \
    notification.Notice.objects.filter(recipient=request.user)
    # Search on sender name
    q = (Q(sender=request.user))
    if q:
        user_notification = user_notification.filter(q)

    count = user_notification.count()
    user_notification_list = \
        user_notification.order_by(sortorder_sign + sortname)[start_page:end_page]

    rows = [{'id': row.id,
             'cell': ['<input type="checkbox" name="select" class="checkbox"\
                      value="' + str(row.id) + '" />',
                      row.id,
                      row.message,
                      str(row.notice_type),
                      str(row.sender),
                      str(row.added),
                      str('<a href="../update_notice_status_cust/' + str(row.id) + '/" class="icon" ' \
                          + call_style(row.unseen) + ' ">&nbsp;</a>'),

             ]}for row in user_notification_list ]

    data = {'rows': rows,
            'page': page,
            'total': count}
    
    return HttpResponse(simplejson.dumps(data), mimetype='application/json',
                        content_type="application/json")



@login_required
def notification_del_read(request, object_id):
    """Delete notification for the logged in user

    **Attributes**:

        * ``object_id`` - Selected notification object
        * ``object_list`` - Selected notification objects

    **Logic Description**:

        * Delete/Mark as Read the selected notification from the notification list
    """
    try:
        # When object_id is not 0
        notification_obj = notification.Notice.objects.get(pk=object_id)
        # Delete/Read notification
        if object_id:
            if request.POST.get('read_all') == 'false':
                request.session["msg_note"] = _('"%(name)s" is deleted successfully.') \
                % {'name': notification_obj.notice_type}
                notification_obj.delete()
            else:
                request.session["msg_note"] = _('"%(name)s" is marked as read successfully.') \
                % {'name': notification_obj.notice_type}
                notification_obj.update(unseen=0)

            return HttpResponseRedirect('/user_detail_change/?selected=2&msg_note=true')
    except:
        # When object_id is 0 (Multiple recrod delete/mark as read)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        notification_list = notification.Notice.objects.extra(where=['id IN (%s)' % values])
        if request.POST.get('read_all') == 'false':
            request.session["msg_note"] = _('%(count)s notification(s) are deleted successfully.')\
            % {'count': notification_list.count()}
            notification_list.delete()
        else:
            request.session["msg_note"] = _('%(count)s notification(s) are marked as read successfully.')\
            % {'count': notification_list.count()}
            notification_list.update(unseen=0)
        return HttpResponseRedirect('/user_detail_change/?selected=2&msg_note=true')


@login_required
def view_notification(request, id):
    """Notice view in detail on Customer UI

    **Attributes**

        * ``template`` - 'frontend/registration/user_notice.html'

    **Logic Description**:

        * User is able to change his/her detail.
    """
    user_notice = notification.Notice.objects.get(pk=id)
    user_notice.unseen = 0
    user_notice.save()
    template = 'frontend/registration/user_notice.html'
    data = {
        'module': current_view(request),
        'notice': user_notice,
        'notice_count': notice_count(request),
        'dialer_setting_msg': user_dialer_setting_msg(request.user),
    }
    return render_to_response(template, data,
           context_instance=RequestContext(request))


def common_notification_status(request, id):
    """Notification Status (e.g. seen/unseen) need to be change.
    It is a common function for admin and customer UI

    **Attributes**:

        * ``pk`` - primary key of notice record

    **Logic Description**:

        * Selected Notification's status need to be changed.
          Changed status can be seen or unseen.
    """
    notice = notification.Notice.objects.get(pk=id)
    if notice.unseen == 1:
        notice.unseen = 0
    else:
        notice.unseen = 1
    notice.save()
    return True


@login_required
def update_notice_status_cust(request, id):
    """Notification Status (e.g. seen/unseen) can be changed from
    customer interface"""
    common_notification_status(request, id)
    return HttpResponseRedirect('/user_detail_change/?selected=2')
