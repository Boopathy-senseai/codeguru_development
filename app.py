from django.shortcuts import render, redirect
from .forms import *
from login.forms import ProfileUpdateForm
from .models import *
from main.models import *
from payment.models import SubscriptionCustomer, website_details
from application.models import *
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseNotModified, HttpResponseRedirect
import json
from django.contrib.auth import login, authenticate, logout
import os, re, time
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
import datetime
from login.decorators import *
import requests
from django.db.models import *
from jobs.filters import *

# from jobs.views import generate_candidate_json,generate_jd_json,matching_api_to_db,remove_case_id,applicant_genarate_json
from jobs.views import (
    generate_candidate_json,
    generate_jd_json,
    remove_case_id,
    applicant_genarate_json,
)
from login.models import *
from users.models import *
from users.serializers import CompanySerializer
from calendarapp.models import *

global countries_to_be_displayed
countries_to_be_displayed = [
    "USA"
]  # if we need to add more countries, the text should be same as the meta of country table in application
global base_dir
from datetime import timedelta, datetime
from zita import settings

base_dir = settings.BASE_DIR
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Aggregate, CharField, Value
from django.core.exceptions import FieldError
from django.db.models.expressions import Subquery
from django.utils import timezone
import pytz
from collections import Counter
import logging
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from collections.abc import Iterable
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import View
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

email_main = settings.EMAIL_HOST_USER
EMAIL_TO = settings.EMAIL_TO
from django.views.decorators.cache import never_cache
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

# from matplotlib_venn import venn2
import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.template.loader import render_to_string

try:
    # import os
    # GTK_FOLDER = r'C:\Program Files\GTK3-Runtime Win64\bin'
    # os.environ['PATH'] = GTK_FOLDER + os.pathsep + os.environ.get('PATH', '')
    from weasyprint import HTML
except:
    pass
from django.http.response import (
    JsonResponse,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotModified,
)
from django.urls import reverse
from random import choice
from string import ascii_lowercase, digits
import time
import ast
import base64
import xmltodict
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from math import pi
import tempfile
import zipfile
import socket

# from scipy.interpolate import interp1d
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jobs_api")
import operator
from django.db.models import Q
from functools import reduce
import requests
import json
from requests.auth import HTTPBasicAuth
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.models import Permission
from users.models import UserHasComapny, CompanyHasInvite, UserDetail
from rest_framework.decorators import api_view
from knox.models import AuthToken
from base64 import b64decode
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from jobs.views import admin_account, user_permission
from calendarapp.models import Event
from email.mime.image import MIMEImage

candi_id = []
from notifications.signals import notify
from notifications.models import Notification
from django.contrib.staticfiles import finders
from itertools import groupby


class YearWeek(Func):
    function = "YEARWEEK"
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


class Concats(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s%(expressions)s)"

    def __init__(self, expression, distinct=False, **extra):
        super(Concats, self).__init__(
            expression,
            distinct="DISTINCT " if distinct else "",
            output_field=CharField(),
            **extra
        )


def mail_notification(
    user_id,
    template,
    message,
    jd_id=None,
    count=None,
    can_id=None,
    code=None,
    company_name=None,
    domain="",
    logo=None,
):
    try:
        user = User_Info.objects.get(user_id=user_id)
    except:
        user = user_id
    htmly = get_template("email_templates/" + template)
    if code != None:
        subject, from_email, to = message, email_main, user.email
        html_content = htmly.render(
            {"user": user, "domain": domain, "code": code, "company_name": company_name}
        )
    elif jd_id == None:
        subject, from_email, to = message, email_main, user.email
        html_content = htmly.render(
            {"user": user, "domain": domain, "company_name": company_name}
        )
    else:
        if can_id == None:
            subject, from_email, to = message, email_main, user.email
            jd_form = JD_form.objects.get(id=jd_id)
            html_content = htmly.render(
                {
                    "user": user,
                    "domain": domain,
                    "jd_form": jd_form,
                    "count": count,
                }
            )
        else:
            jd_form = JD_form.objects.get(id=jd_id)
            count = (
                jd_candidate_analytics.objects.filter(jd_id=jd_id, status_id_id=1)
                .values("candidate_id_id")
                .distinct()
                .count()
            )
            subject, from_email, to = message, email_main, jd_form.user_id.email
            can_id = Personal_Info.objects.get(application_id=can_id)
            html_content = htmly.render(
                {
                    "user": jd_form.user_id,
                    "domain": domain,
                    "jd_form": jd_form,
                    "count": count,
                    "can_id": can_id,
                }
            )
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    if logo == True:
        image_data = [
            "twitter.png",
            "linkedin.png",
            "youtube.png",
            "new_zita_white.png",
        ]
        for i in image_data:
            msg.attach(logo_data(i))
    msg.mixed_subtype = "related"

    try:
        msg.send()
    except:
        pass


# Initial page load api with basic data


class country(generics.GenericAPIView):
    def get(self, request):
        country_list = []
        country = tmeta_currency_type.objects.all()
        for i in country:
            country_list.append({"value": i.id, "label": i.value})

        return Response(country_list)


class job_post_confirmation(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk)
        import time

        time.sleep(120)
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=5, is_active=True
        ).exists():
            try:
                pass
                # result=matching_api_to_db(request,jd_id=pk,can_id=None)
            except Exception as e:
                logger.error("Error in the matching : " + str(e))
            jd = jd.annotate(
                zita_match=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id_id=5,
                        candidate_id__first_name__isnull=False,
                        candidate_id__email__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("status_id")
                    .annotate(cout=Count("candidate_id"))[:1]
                    .values("cout"),
                    output_field=CharField(),
                ),
            )
            zita_match_candidate = zita_match_candidates.objects.filter(
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                jd_id=jd[0],
            )[:3]
            domain = settings.CLIENT_URL
            zita_match_candidate = zita_match_candidate.annotate(
                image=Subquery(
                    Profile.objects.filter(
                        user_id=OuterRef("candidate_id__candidate_id__user_id")
                    )[:1].values("image")
                ),
                match=Subquery(
                    Matched_candidates.objects.filter(
                        jd_id=OuterRef("jd_id"), candidate_id=OuterRef("candidate_id")
                    )[:1].values("profile_match")
                ),
            )
            career_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
            context = {
                "jd_form": jd[0],
                "zita_match": zita_match_candidate,
                "career_url": career_url,
                "domain": domain,
            }
            email = get_template("email_templates/job_post_confirmation.html")
            email = email.render(context)
            msg = EmailMultiAlternatives(
                "Congratulations!!! Your job has been successfully posted on your career page",
                email,
                settings.EMAIL_HOST_USER,
                ["rajas@zita.ai"],
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
                "default.jpg",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            for p in zita_match_candidate:
                if p.image != None and p.image != "default.jpg":
                    msg.attach(profile(p.image))
            msg.mixed_subtype = "related"
            msg.send()
        return Response({"success": True})


def logo_data(img):
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def profile(prof):
    with open(settings.BASE_DIR + "/media/" + prof, "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", prof)
    return logo


class notification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        # user = request.user
        user, updated_by = admin_account(self.request)
        unread = user.notifications.filter(deleted=0)
        has_permission = user_permission(self.request, "bulkImport_candidates")
        if not has_permission == True:
            unread = unread.exclude(description="bulkimport")
        today_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = datetime.now() + timezone.timedelta(days=1)
        end_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_time = datetime.now() - timezone.timedelta(days=1)
        yesterday_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_time_last = yesterday_time + timezone.timedelta(days=1)
        yesterday_time_last = yesterday_time_last.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        total = user.notifications.filter(unread=1).count()
        today = unread.filter(timestamp__range=(today_time, end_time))
        yesterday = unread.filter(
            timestamp__range=(yesterday_time, yesterday_time_last)
        )
        others = unread.filter(timestamp__date__lte=yesterday_time)
        # data= 'Test'
        # target_object_id= 69
        # action_object_object_id = 695
        # description='applicant'
        data = {
            "success": True,
            "today": today.values(),
            "yesterday": yesterday.values(),
            "others": others.values(),
            "total_unread": total,
            "total": unread.count(),
        }
        return Response(data)

    def post(self, request):
        request = self.request
        user = request.user
        pk = request.POST["id"]
        Notification.objects.filter(id=pk).update(unread=0)
        data = {
            "success": True,
        }
        return Response(data)

    def delete(self, request):
        request = self.request
        user = request.user
        user.notifications.all().update(deleted=1, unread=0)
        data = {
            "success": True,
        }
        return Response(data)


class zita_talent_pool_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)
        has_permission = user_permission(self.request, "talent_sourcing")

        # page permisson check
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})

        permission = Permission.objects.filter(user=self.request.user).values_list(
            "codename", flat=True
        )

        # stripe checkout responce and updating the data
        if "session_id" in self.request.GET:
            import stripe

            stripe.api_key = settings.STRIPE_SECRET_KEY
            session_id = self.request.GET["session_id"]
            checkout = stripe.checkout.Session.retrieve(
                session_id,
            )

            metadata = checkout.get("metadata")
            product_name = metadata["product_name"]
            quantity = metadata["quantity"]
            if product_name == "Source_Credit":
                try:
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=11
                    ).available_count
                except client_features_balance.DoesNotExist:
                    client_features_balance.objects.create(
                        client_id=user_id, feature_id_id=11, available_count=0
                    )
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=11
                    ).available_count
                total = int(quantity) + available_count
                client_features_balance.objects.filter(
                    client_id=user_id, feature_id_id=11
                ).update(available_count=total)
                client_addons_purchase_history.objects.create(
                    client_id=user_id,
                    feature_id_id=11,
                    purchased_count=int(quantity),
                )
        show_pop = 0
        if "session_id" in self.request.GET:
            show_pop = 1
        elif "cancelled" in self.request.GET:
            show_pop = 2
        else:
            show_pop = 0

        # retrieve data form DB for initial page load
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candi_limit = 0
        state_list = list(
            State.objects.filter(country_id=231).values_list("name", flat=True)
        )
        location_id = State.objects.filter(country_id=231).values_list("id", flat=True)
        city_list = list(
            City.objects.filter(state_id__in=location_id).values_list("name", flat=True)
        )
        location = state_list + city_list
        context = {
            "show_pop": show_pop,
            "source_limit": source_limit,
            "source_limit": source_limit,
            "permission": list(permission),
            "location": location,
        }
        return Response(context)


# talent pool search data


class zita_talent_pool_search_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)

        # Search query for RL API
        if len(self.request.GET["keywords"]) > 0:
            try:
                countries_states = pd.read_csv(
                    base_dir + "/" + "media/countries_states.csv"
                )
            except:
                countries_states = pd.read_csv(
                    os.getcwd() + "/" + "media/countries_states.csv"
                )
            if (
                self.request.GET["location"].lower()
                in countries_states["state"].to_list()
            ):
                location = "state of " + self.request.GET["location"]
            else:
                location = self.request.GET["location"]

            data = {
                "keywords": self.request.GET["keywords"],
                "partner_user_ref": "zita-" + str(user_id.id),
                "location": location,
                "radius": self.request.GET["radius"],
                "active_within_days": self.request.GET["last_active"],
                "limit": 500,
            }

            data_rl = RL_search_api(data)
        else:
            data_rl = User.objects.none()

        # retrieve data form DB for access the cards
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candi_limit = 0
        candi_list = employer_pool.objects.filter(
            client_id=user_id, can_source_id=2
        ).values_list("candi_ref_id", flat=True)
        plan = subscriptions.objects.filter(client_id=user_id, is_active=True).values()
        context = {
            "data": data_rl,
            "source_limit": source_limit,
            "candi_limit": candi_limit,
            "plan": list(plan),
            "candi_list": list(candi_list),
        }
        return Response(context)


# bulk unlock and download api for talent pool


class bulk_action_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        candi_list = request.GET["candi_list"].split(",")

        # bulk download function
        if "download" in request.GET:
            t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
            with zipfile.ZipFile(
                base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "w"
            ) as myzip:
                for i in candi_list:
                    if not i == "false":
                        try:
                            # unlock API call
                            url = (
                                "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
                                + i
                                + "/all/zita-"
                                + str(user_id.id)
                            )

                            result = requests.get(
                                url, auth=(settings.rl_username, settings.rl_password)
                            )
                            result = json.loads(result.content)
                            try:
                                data = result["result"]["pages"][0]["content"]
                            except:
                                data = result["result"]["pages"]["content"]
                            byte = b64decode(data, validate=True)

                            # processing the encoded data to file
                            if byte[0:4] != b"%PDF":
                                raise ValueError("Missing the PDF file signature")
                            f = open(
                                base_dir
                                + "/media/"
                                + result["first_name"]
                                + "_"
                                + result["id"]
                                + ".pdf",
                                "wb",
                            )
                            f.write(byte)
                            f.close()
                            myzip.write(
                                base_dir
                                + "/media/"
                                + result["first_name"]
                                + "_"
                                + result["id"]
                                + ".pdf",
                                result["first_name"] + "_" + result["id"] + ".pdf",
                            )

                        except Exception as e:
                            logger.error("Bulk download file error ---- " + str(e))

            # converting zip file
            myzip.close()
            file = open(
                base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "rb"
            )
            response = HttpResponse(file, content_type="application/zip")
            response["Content-Disposition"] = (
                "attachment; filename=Candidates_Profiles_" + str(t) + ".zip"
            )
            domain = get_current_site(request)
            return JsonResponse(
                {
                    "file_path": str(domain)
                    + "/media/Candidates_Profiles_"
                    + str(t)
                    + ".zip"
                }
            )

        # bulk unlock function
        elif "unlock" in request.GET:
            t = datetime.now()
            unlock_can_list = []

            # unlock access validation
            if not "manage_account_settings" in permission:
                data = {"success": "no_permission"}
                return JsonResponse(data)
            try:

                source = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                )
            except:
                data = {"success": "no_count"}
                return JsonResponse(data)

            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            )

            if candi_limit.available_count != None:
                if (
                    candi_limit.available_count == 0
                    or candi_limit.available_count < len(candi_list)
                ):
                    data = {"success": "no_count"}
                    return JsonResponse(data)
            if source.available_count < len(candi_list):
                data = {"success": "no_limit"}
                return JsonResponse(data)
            else:
                source_limit = source.available_count
            if candi_limit.available_count != None:
                if candi_limit.available_count < len(candi_list):
                    data = {"success": "no_limit"}
                    return JsonResponse(data)
            count = 0
            for i in candi_list:
                if not i == "false":

                    try:

                        # unlock API call
                        url = (
                            "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
                            + i
                            + "/all/zita-"
                            + str(user_id.id)
                        )

                        result = requests.get(
                            url, auth=(settings.rl_username, settings.rl_password)
                        )
                        result = json.loads(result.content)
                        t = datetime.now()
                        try:
                            data = result["result"]["pages"][0]["content"]
                        except:
                            data = result["result"]["pages"]["content"]

                        # processing the encoded data to file
                        byte = b64decode(data, validate=True)
                        if byte[0:4] != b"%PDF":
                            raise ValueError("Missing the PDF file signature")
                        file = open(
                            base_dir
                            + "/media/unlock/"
                            + result["first_name"]
                            + "_"
                            + result["id"]
                            + ".pdf",
                            "wb",
                        )
                        file.write(byte)
                        file.close()
                        try:
                            job_type = tmeta_job_type.objects.get(
                                label_name=result["job_type"]
                            )
                        except:
                            job_type = None

                        relocate = None
                        if result["willing_to_relocate"] == "Yes":
                            relocate = True
                        elif result["willing_to_relocate"] == "No":
                            relocate = False
                        state = result["town"].split(",")[1]
                        city = result["town"].split(",")[0]
                        try:
                            countries_states = pd.read_csv(
                                base_dir + "/" + "media/countries_states.csv"
                            )
                        except:
                            countries_states = pd.read_csv(
                                os.getcwd() + "/" + "media/countries_states.csv"
                            )

                        for i in range(len(countries_states["state_code"])):
                            if (
                                countries_states["state_code"][i]
                                == state.strip().lower()
                            ):
                                state = countries_states["state"][i]
                        location = city + ", " + state.upper()

                        # store data to DB
                        if employer_pool.objects.filter(
                            email=result["email"], client_id=user_id
                        ).exists():
                            employer_pool.objects.filter(email=result["email"]).update(
                                can_source_id=2,
                                client_id=user_id,
                                updated_by=updated_by,
                                candidate_id=None,
                                job_type=job_type,
                                first_name=result["first_name"],
                                last_name=result["last_name"],
                                email=result["email"],
                                candi_ref_id=result["id"],
                                work_exp=result["work_experience"],
                                relocate=relocate,
                                qualification=result["educational_level"],
                                exp_salary=str(result["min_expected_salary"])
                                + " - "
                                + str(result["max_expected_salary"]),
                                job_title=result["desired_job_title"],
                                skills=",".join(result["key_skills"]),
                                location=location,
                            )
                            emp_pool = employer_pool.objects.get(
                                email=result["email"], client_id=user_id
                            )
                        else:
                            employer_pool.objects.create(
                                can_source_id=2,
                                client_id=user_id,
                                updated_by=updated_by,
                                candidate_id=None,
                                job_type=job_type,
                                candi_ref_id=result["id"],
                                first_name=result["first_name"],
                                last_name=result["last_name"],
                                email=result["email"],
                                work_exp=result["work_experience"],
                                relocate=relocate,
                                qualification=result["educational_level"],
                                exp_salary=str(result["min_expected_salary"])
                                + " - "
                                + str(result["max_expected_salary"]),
                                job_title=result["desired_job_title"],
                                skills=",".join(result["key_skills"]),
                                location=location,
                            )
                            emp_pool = employer_pool.objects.filter(
                                client_id=user_id,
                                email=result["email"],
                            ).last()
                        unlock_can_list.append(
                            str(emp_pool.id)
                            + "@@"
                            + result["first_name"]
                            + "_"
                            + result["id"]
                        )
                        count = count + 1

                    except Exception as e:
                        logger.error("Unlock file Error ---- " + str(e))

            # updating the details in DB
            source.available_count = source.available_count - count
            source.save()
            if candi_limit.available_count != None:
                candi_limit.available_count = candi_limit.available_count - count
                candi_limit.save()
                candi_limit = candi_limit.available_count
            else:
                candi_limit = "Unlimited"
            if count > 0:
                if count == 1:
                    UserActivity.objects.create(
                        user=request.user,
                        action_id=4,
                        action_detail=str(count) + " candidate from Talent Sourcing",
                    )
                else:
                    UserActivity.objects.create(
                        user=request.user,
                        action_id=4,
                        action_detail=str(count) + " candidates from Talent Sourcing",
                    )

            try:
                source = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                ).available_count
            except:
                source = 0
            candi_list = employer_pool.objects.filter(
                client_id=user_id, can_source_id=2
            ).values_list("candi_ref_id", flat=True)
            data = {
                "success": True,
                "unlock_can_list": unlock_can_list,
                "candi_list": list(candi_list),
                "source_limit": source,
                "candi_limit": candi_limit,
            }
            return Response(data)
        else:
            return Response(
                {
                    "success": False,
                }
            )


# single unlock candidates


class unlock_candidates_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request
        user_id, updated_by = admin_account(request)

        # unlock  validation
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        if not "manage_account_settings" in permission:
            data = {"success": "no_permission"}
            return JsonResponse(data)
        candi_limit = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=12
        )
        if candi_limit.available_count == 0:
            data = {"success": "no_count"}
            return JsonResponse(data)
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            )
            if source_limit.available_count == 0:
                data = {"success": "no_limit"}
                return JsonResponse(data)
        except:
            data = {"success": False}
            return JsonResponse(data)

        # API call
        candidate_key = request.GET["key"]
        url = (
            "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
            + candidate_key
            + "/all/zita-"
            + str(user_id.id)
        )
        unlock_can_list = []
        result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
        result = json.loads(result.content)

        # Data processing
        try:
            data = result["result"]["pages"][0]["content"]
        except:
            data = result["result"]["pages"]["content"]
        byte = b64decode(data, validate=True)
        if byte[0:4] != b"%PDF":
            raise ValueError("Missing the PDF file signature")
        file = open(
            base_dir
            + "/media/unlock/"
            + result["first_name"]
            + "_"
            + result["id"]
            + ".pdf",
            "wb",
        )
        file.write(byte)
        file.close()
        try:
            job_type = tmeta_job_type.objects.get(label_name=result["job_type"])
        except:
            job_type = None

        relocate = None
        if result["willing_to_relocate"] == "Yes":
            relocate = True
        elif result["willing_to_relocate"] == "No":
            relocate = False
        state = result["town"].split(",")[1]
        city = result["town"].split(",")[0]
        try:
            countries_states = pd.read_csv(
                base_dir + "/" + "media/countries_states.csv"
            )
        except:
            countries_states = pd.read_csv(
                os.getcwd() + "/" + "media/countries_states.csv"
            )

        for i in range(len(countries_states["state_code"])):
            if countries_states["state_code"][i] == state.strip().lower():
                state = countries_states["state"][i]
        location = city + ", " + state.upper()

        # Stroing DB
        if employer_pool.objects.filter(
            email=result["email"], client_id=user_id
        ).exists():
            employer_pool.objects.filter(email=result["email"]).update(
                can_source_id=2,
                client_id=user_id,
                updated_by=updated_by,
                candidate_id=None,
                job_type=job_type,
                first_name=result["first_name"],
                last_name=result["last_name"],
                email=result["email"],
                work_exp=result["work_experience"],
                relocate=relocate,
                candi_ref_id=result["id"],
                qualification=result["educational_level"],
                exp_salary=str(result["min_expected_salary"])
                + " - "
                + str(result["max_expected_salary"]),
                job_title=result["desired_job_title"],
                skills=",".join(result["key_skills"]),
                location=location,
            )
            emp_pool = employer_pool.objects.get(
                email=result["email"], client_id=user_id
            )
        else:
            employer_pool.objects.create(
                can_source_id=2,
                client_id=user_id,
                updated_by=updated_by,
                candidate_id=None,
                job_type=job_type,
                candi_ref_id=result["id"],
                first_name=result["first_name"],
                last_name=result["last_name"],
                email=result["email"],
                work_exp=result["work_experience"],
                relocate=relocate,
                qualification=result["educational_level"],
                exp_salary=str(result["min_expected_salary"])
                + " - "
                + str(result["max_expected_salary"]),
                job_title=result["desired_job_title"],
                skills=",".join(result["key_skills"]),
                location=location,
            )
            emp_pool = employer_pool.objects.filter(
                email=result["email"], client_id=user_id
            ).last()

        # update the count in DB
        unlock_can_list.append(
            str(emp_pool.id) + "@@" + result["first_name"] + "_" + result["id"]
        )
        source_limit.available_count = source_limit.available_count - 1
        source_limit.save()
        source_limit = source_limit.available_count
        if candi_limit.available_count != None:
            candi_limit.available_count = candi_limit.available_count - 1
            candi_limit.save()
            candi_limit = candi_limit.available_count
        else:
            candi_limit = "Unlimited"

        UserActivity.objects.create(
            user=request.user,
            action_id=4,
            action_detail="1 candidate from Talent Sourcing",
        )
        candi_list = employer_pool.objects.filter(
            client_id=user_id, can_source_id=2
        ).values_list("candi_ref_id", flat=True)

        data = {
            "success": True,
            "unlock_can_list": unlock_can_list,
            "source_limit": source_limit,
            "candi_list": list(candi_list),
            "candi_limit": candi_limit,
        }
        return Response(data)


# Background parsing API
@api_view(["GET", "POST"])
def parsed_text_api(request):
    try:
        unlock_can_list = request.GET["unlock_can_list"].split(",")
        for i in unlock_can_list:
            emp_pool_id = i.split("@@")[0]
            talent_pool_id = i.split("@@")[1]

            # Parsing function
            parser_output = resume_parsing(str(talent_pool_id) + ".pdf")

            # storing parsed data to DB
            if candidate_parsed_details.objects.filter(
                candidate_id_id=int(emp_pool_id)
            ).exists():

                candidate_parsed_details.objects.filter(
                    candidate_id_id=int(emp_pool_id)
                ).update(
                    candidate_id_id=int(emp_pool_id),
                    parsed_text=parser_output,
                    resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
                )
            else:
                candidate_parsed_details.objects.create(
                    candidate_id_id=int(emp_pool_id),
                    parsed_text=parser_output,
                    resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
                )
            result = generate_candidate_json(request, pk=int(emp_pool_id))
        data = {"success": True}
    except Exception as e:
        data = {"success": False, "Error": str(e)}
    return JsonResponse(data)


# Parsing function
def resume_parsing(filename):
    headers = {"Authorization": settings.rp_api_auth_token}

    url = settings.rp_api_url

    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/unlock/" + filename, "rb")
        }
    except:

        files = {"resume_file": open(base_dir + "/" + "media/unlock/" + filename, "rb")}
    result = requests.post(url, headers=headers, files=files)
    respone_json = json.loads(result.content)

    try:
        parser_output = respone_json["result_dict"]
    except:
        parser_output = {}

    return parser_output


# searching api call in RL
def RL_search_api(data):
    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(
            settings.rl_search_url,
            json=data,
            headers=headers,
            auth=(settings.rl_username, settings.rl_password),
        )
        result = json.loads(result.content)
        data_rl = result["candidates"]
    except:
        data_rl = None

    return data_rl


def parsing_rl(filename):
    headers = {"Authorization": settings.rp_api_auth_token}

    url = settings.rp_api_url
    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/resume/" + filename, "rb")
        }
    except:

        files = {"resume_file": open(base_dir + "/" + "media/resume/" + filename, "rb")}
    result = requests.post(url, headers=headers, files=files)
    respone_json = json.loads(result.content)
    try:
        r_data = respone_json["file_data"]
    except:
        r_data = {}

    try:
        sample = respone_json["result_dict"]
    except:
        sample = {}
    try:
        sentence_list = respone_json["sentence_list"]
    except:
        sentence_list = "[]"

    try:
        with open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json", "w") as fp:
            json.dump(sample, fp)
        with open(
            base_dir + "/" + "media/SOT_OUT/" + filename + "_data.json", "w"
        ) as fp:
            json.dump(r_data, fp)
    except:
        with open(os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json", "w") as fp:
            json.dump(sample, fp)
        with open(
            os.getcwd() + "/" + "media/SOT_OUT/" + filename + "_data.json", "w"
        ) as fp:
            json.dump(r_data, fp)

    return sentence_list


class url_verification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        url = request.GET["url"]
        data = {}
        data["success"] = 0
        if career_page_setting.objects.filter(career_page_url=url).exists():
            data["success"] = 1
        return Response(data)


# candidate view api for talent pool
@api_view(["GET", "POST"])
def candidate_view_api(request):
    unlock_can_list = []
    user_id, updated_by = admin_account(request)
    candidate_key = request.GET["key"]
    url = (
        "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
        + candidate_key
        + "/all/zita-"
        + str(user_id.id)
    )

    result = requests.get(url, auth=("975486", "a4afe1a58d53"))
    result = json.loads(result.content)
    data = result["result"]["pages"][0]["content"]
    byte = b64decode(data, validate=True)
    main_url = request.build_absolute_uri("/")
    if byte[0:4] != b"%PDF":
        raise ValueError("Missing the PDF file signature")
    try:
        f = open(base_dir + "/" + "media/data.pdf", "wb")
    except:
        f = open(os.getcwd() + "/" + "media/data.pdf", "wb")
    f.write(byte)
    f.close()
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    context = {
        "file": str(main_url) + "media/data.pdf",
        "permission": permission,
        "candidate_key": candidate_key,
        "unlock_status": result["unlock_status"],
    }

    return Response(context)


@api_view(["GET", "POST"])
def what_jobs_posting(request):
    if request.method == "POST":
        # pk = 569
        pk = request.POST["pk"]
        jd_details = JD_form.objects.get(id=pk)
        location = JD_locations.objects.get(jd_id_id=pk)
        user_id, updated_by = admin_account(request)
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        career_page_url = career_page_setting.objects.get(
            recruiter_id=user_id
        ).career_page_url
        main_url = get_current_site(request).domain
        data = {}
        data["command"] = "add"
        data["title"] = jd_details.job_title
        data["title"] = jd_details.job_title
        if jd_details.job_type.id in [1, 4, 5]:
            data["job_type"] = "Permanent"
            data["job_status"] = "full-time"
        else:
            data["job_type"] = jd_details.job_type.label_name
            data["job_status"] = "full-time"
        data["description"] = jd_details.richtext_job_description
        if jd_details.show_sal_to_candidate == True:
            data["salary_from"] = jd_details.salary_min
            data["salary_to"] = jd_details.salary_max

        data["location"] = (
            location.country.name
            + ", "
            + location.state.name
            + ", "
            + location.city.name
        )
        data["application_url"] = (
            "http://"
            + main_url
            + "/"
            + career_page_url
            + "/job-view/"
            + str(jd_details.id)
            + "/"
            + str(jd_details.job_title)
        )
        # data['application_url'] = 'http://staging.zita.ai/gvtech1/job-view/306/Front%20End%20Developer'
        data["company_email"] = request.user.email
        data["company_name"] = company_name
        data["company_name"] = company_name
        data["reference"] = jd_details.job_id
        if jd_details.job_type.id != 3:
            data["salary_type"] = "annum"
        else:
            data["salary_type"] = "hour"
        url = settings.what_jobs_posting_url
        headers = {"x-api-token": settings.what_jobs_token}
        result = requests.post(
            url, headers=headers, files={"data": (None, json.dumps([data]))}
        )
        try:
            result = json.loads(result.content)
            result = result[0]["response"]
            external_jobpostings_by_client.objects.get_or_create(
                client_id=user_id,
                ext_jp_site_id_id=2,
                jd_id_id=pk,
                posted_by=request.user.username,
                jobposting_url=result["job_url"],
                job_posting_ref_id=result["job_id"],
            )
            result = {"success": True, "out_data": result}
        except Exception as e:
            logger.error(
                "Error in resume-library job posting, Error -- "
                + str(e)
                + "JD-ID -- "
                + str(pk)
            )
            result = {"success": False, "out_data": False}
    return JsonResponse(result)


@api_view(["GET", "POST"])
def remove_what_jobs_posting(request):
    pk = request.GET["pk"]
    try:
        external_jobs = external_jobpostings_by_client.objects.get(
            jd_id_id=pk, is_active=True, ext_jp_site_id_id=2
        )
    except:
        external_jobs = None
    if external_jobs != None:
        try:
            data = [
                {
                    "job_id": str(external_jobs.job_posting_ref_id),
                    "command": "delete",
                }
            ]
            url = settings.what_jobs_posting_url
            headers = {"x-api-token": settings.what_jobs_token}
            result = requests.post(
                url, headers=headers, files={"data": (None, json.dumps(data))}
            )
            result = json.loads(result.content)
        except:
            logger.error(
                "Error in resume-library job remove, Error -- "
                + str(e)
                + "JD-ID -- "
                + str(pk)
            )
        external_jobs.is_active = False
        external_jobs.job_inactivated_on = datetime.now()
        external_jobs.job_inactivated_by = request.user.username
        external_jobs.save()
        result = {"success": True, "out_data": result}
    else:
        result = {"success": False, "out_data": False}
    return JsonResponse(result)


class applicants_profile_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        has_permission = user_permission(self.request, "applicants")
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})
        user_id, updated_by = admin_account(self.request)
        can_id = self.request.GET["can_id"]
        if int(self.request.GET["jd_id"]) != 0:
            jd_id = self.request.GET["jd_id"]
        else:
            jd_id = None
        candidate_details = employer_pool.objects.filter(id=can_id)
        jd = JD_form.objects.filter(id=jd_id)

        status_id = applicants_status.objects.filter(
            jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[1, 2, 3, 4, 7]
        ).values()

        try:
            source = (
                applicants_status.objects.filter(jd_id_id=jd_id, candidate_id_id=can_id)
                .exclude(status_id_id=6)
                .last()
                .source
            )
        except:
            source = "Career Page"
        try:
            chatname = (
                str(candidate_details[0].client_id.id)
                + "-"
                + str(candidate_details[0].candidate_id.user_id.id)
            )
        except:
            chatname = ""

        applicants_status.objects.get_or_create(
            jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=6, client_id=user_id
        )
        if jd_id == None:
            jd = None
        else:
            jd = JD_form.objects.filter(id=jd_id).values()[0]

        if candidate_details[0].candidate_id != None:

            candidate_details = candidate_details.annotate(
                image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                        :1
                    ].values("image")
                ),
                file=Subquery(
                    Myfiles.objects.filter(upload_id=OuterRef("candidate_id__user_id"))
                    .order_by("-id")[:1]
                    .values("resume_file")
                ),
            )
            total_exp = Additional_Details.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            experience = Experiences.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            education = Education.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            personalInfo = Personal_Info.objects.filter(
                application_id=candidate_details[0].candidate_id.pk
            ).values(
                "firstname",
                "lastname",
                "email",
                "contact_no",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "Date_of_birth",
                "linkedin_url",
                "career_summary",
                "gender",
                "updated_at",
                "code_repo",
                "visa_sponsorship",
                "remote_work",
                "type_of_job__label_name",
                "available_to_start__label_name",
                "industry_type__label_name",
                "desired_shift__label_name",
                "curr_gross",
                "current_currency",
                "exp_gross",
                "salary_negotiable",
                "current_country__name",
                "current_state__name",
                "current_city__name",
                "current1_country",
                "current2_country",
                "current3_country",
                "relocate",
            )
            project = Projects.objects.filter(
                application_id=candidate_details[0].candidate_id, work_proj_type=False
            ).values()
            ac_project = Projects.objects.filter(
                application_id=candidate_details[0].candidate_id, work_proj_type=True
            ).values()
            skills = Skills.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            fresher = Fresher.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            course = Certification_Course.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            contrib = Contributions.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values(
                "application_id",
                "contrib_text",
                "contrib_type__label_name",
            )
            questionnaire = applicant_questionnaire.objects.filter(jd_id_id=jd_id)
            questionnaire = questionnaire.annotate(
                answer=Subquery(
                    applicant_answers.objects.filter(
                        qus_id=OuterRef("id"),
                        candidate_id=candidate_details[0].candidate_id,
                    )[:1].values("answer")
                ),
            ).values()
            cover_letter = applicant_cover_letter.objects.filter(
                candidate_id=candidate_details[0].candidate_id,
                jd_id_id=jd_id,
            ).values()
            context = {
                "applicant": True,
                "success": True,
                "candidate_details": candidate_details.values(),
                "jd_id": jd_id,
                "can_id": can_id,
                "course": course,
                "contrib": contrib,
                "chatname": chatname,
                "source": source,
                "skills": skills,
                "education": education,
                "project": project,
                "questionnaire": questionnaire,
                "ac_project": ac_project,
                "fresher": fresher,
                "cover_letter": cover_letter,
                "total_exp": total_exp,
                "experience": experience,
                "status_id": status_id,
                "jd": jd,
                "personalInfo": personalInfo,
            }
        else:
            candidate_details = candidate_details.annotate(
                file=Subquery(
                    candidate_parsed_details.objects.filter(candidate_id=OuterRef("id"))
                    .order_by("id")[:1]
                    .values("resume_file_path")
                ),
            )
            context = {
                "success": True,
                "applicant": False,
                "candidate_details": candidate_details.values(),
                "jd_id": jd_id,
                "can_id": can_id,
                "chatname": chatname,
                "source": source,
                "status_id": status_id,
                "jd": jd,
            }
        return Response(context)


class applicants_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        request = self.request
        pk = jd_id
        user_id, updated_by = admin_account(request)
        try:
            skill_list = open(base_dir + "/" + "media/skills.csv", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
        skill_list = skill_list.read()
        skill_list = skill_list.split("\n")
        today = timezone.now().date
        applicants = applicants_status.objects.filter(jd_id_id=pk)
        jd_list = get_object_or_404(JD_form, id=pk)
        fav = jd_list.favourite.all()
        applicants = applicants.annotate(
            fav=Subquery(fav.filter(id=OuterRef("candidate_id"))[:1].values("id")),
            name=Subquery(
                applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                    "candidate_id__candidate_id__firstname"
                )
            ),
            email=Subquery(
                applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                    "candidate_id__email"
                )
            ),
            qualification=Subquery(
                applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                    "candidate_id__qualification"
                )
            ),
            skills=Subquery(
                applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                    "candidate_id__skills"
                )
            ),
            event=Subquery(
                Event.objects.filter(
                    attendees__in=OuterRef("candidate_id__email"), user=request.user
                )[:1].values("id")
            ),
            location=Subquery(
                applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                    "candidate_id__location"
                )
            ),
            viewed=Subquery(
                applicants_status.objects.filter(
                    candidate_id=OuterRef("candidate_id"),
                    client_id=user_id,
                    status_id_id=6,
                )[:1].values("candidate_id__location")
            ),
            work_exp=Subquery(
                Additional_Details.objects.filter(
                    application_id=OuterRef("candidate_id__candidate_id")
                )[:1].values("total_exp_year")
            ),
            match=Subquery(
                Matched_candidates.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("candidate_id")
                )[:1].values("profile_match")
            ),
            image=Subquery(
                Profile.objects.filter(
                    user_id=OuterRef("candidate_id__candidate_id__user_id")
                )[:1].values("image")
            ),
            file=Subquery(
                Myfiles.objects.filter(
                    upload_id=OuterRef("candidate_id__candidate_id__user_id")
                )
                .order_by("-id")[:1]
                .values("resume_file")
            ),
        ).order_by("-created_on")

        if "profile_match" in request.GET and len(request.GET["profile_match"]) > 0:
            try:
                if len(request.GET["profile_match"]) > 0:
                    data_profile = request.GET["profile_match"].split("-")
                    request.GET._mutable = True
                    request.GET["match_min"] = data_profile[0]
                    request.GET["match_max"] = data_profile[1]
                    if data_profile[1] == "60":
                        applicants = applicants.filter(
                            Q(
                                match__range=(
                                    request.GET["match_min"],
                                    request.GET["match_max"],
                                )
                            )
                            | Q(match__isnull=True)
                        )
                    else:
                        applicants = applicants.filter(
                            match__range=(
                                request.GET["match_min"],
                                request.GET["match_max"],
                            )
                        )
            except:
                request.GET._mutable = True
                request.GET["profile_match"] = ""
        fav_id = False
        if "fav" in request.GET and len(request.GET["fav"]) > 0:
            if request.GET["fav"] == "add":
                fav_id = True
                applicants = applicants.exclude(fav__isnull=True)
        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                applicants = applicants.filter(
                    email__icontains=request.GET["candidate"]
                )
            else:
                applicants = applicants.filter(name__icontains=request.GET["candidate"])
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            data_profile = request.GET["work_experience"].split("-")
            request.GET._mutable = True
            request.GET["work_min"] = data_profile[0]
            request.GET["work_max"] = data_profile[1]
            applicants = applicants.filter(
                work_exp__range=(
                    int(request.GET["work_min"]),
                    int(request.GET["work_max"]),
                )
            )
        if "profile_view" in request.GET and len(request.GET["profile_view"]) > 0:
            if request.GET["profile_view"] == "1":
                applicants = applicants.exclude(viewed__isnull=True)
            elif request.GET["profile_view"] == "0":
                applicants = applicants.exclude(viewed__isnull=False)
        if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            applicants = applicants.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            applicants = applicants.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
                )
            )
        request.GET._mutable = True
        if "sort_applicant" in request.GET:
            if len(request.GET.getlist("sort_applicant")) > 1:
                request.GET["sort_applicant"] = request.GET.getlist("sort_applicant")[0]
            if request.GET["sort_applicant"] == "date":
                applicant = applicants.filter(status_id_id=1).order_by("-created_on")
            elif request.GET["sort_applicant"] == "name":
                applicant = applicants.filter(status_id_id=1).order_by("name")
            else:
                applicant = applicants.filter(status_id_id=1).order_by("-match")
        else:
            applicant = applicants.filter(status_id_id=1)
        if "sort_shortlisted" in request.GET:
            if len(request.GET.getlist("sort_shortlisted")) > 1:
                request.GET["sort_shortlisted"] = request.GET.getlist(
                    "sort_shortlisted"
                )[0]
            if request.GET["sort_shortlisted"] == "date":
                shortlisted = applicants.filter(status_id_id=2).order_by("-created_on")
            elif request.GET["sort_shortlisted"] == "name":
                shortlisted = applicants.filter(status_id_id=2).order_by("name")
            else:
                shortlisted = applicants.filter(status_id_id=2).order_by("-match")
        else:
            shortlisted = applicants.filter(status_id_id=2)
        if "sort_interviewed" in request.GET:
            if len(request.GET.getlist("sort_interviewed")) > 1:
                request.GET["sort_interviewed"] = request.GET.getlist(
                    "sort_interviewed"
                )[0]
            if request.GET["sort_interviewed"] == "date":
                interviewed = applicants.filter(status_id_id=3).order_by("-created_on")
            elif request.GET["sort_interviewed"] == "name":
                interviewed = applicants.filter(status_id_id=3).order_by("name")
            else:
                interviewed = applicants.filter(status_id_id=3).order_by("-match")
        else:
            interviewed = applicants.filter(status_id_id=3)
        if "sort_selected" in request.GET:
            if len(request.GET.getlist("sort_selected")) > 1:
                request.GET["sort_selected"] = request.GET.getlist("sort_selected")[0]
            if request.GET["sort_selected"] == "date":
                selected = applicants.filter(status_id_id=4).order_by("-created_on")
            elif request.GET["sort_selected"] == "name":
                selected = applicants.filter(status_id_id=4).order_by("name")
            else:
                selected = applicants.filter(status_id_id=4).order_by("-match")
        else:
            selected = applicants.filter(status_id_id=4)
        if "sort_rejected" in request.GET:
            if len(request.GET.getlist("sort_rejected")) > 1:
                request.GET["sort_rejected"] = request.GET.getlist("sort_rejected")[0]
            if request.GET["sort_rejected"] == "date":
                rejected = applicants.filter(status_id_id=7).order_by("-created_on")
            elif request.GET["sort_rejected"] == "name":
                rejected = applicants.filter(status_id_id=7).order_by("name")
            else:
                rejected = applicants.filter(status_id_id=7).order_by("-match")
        else:
            rejected = applicants.filter(status_id_id=7)

        get_dict_copy = request.GET.copy()
        params = get_dict_copy.urlencode()
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_google.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json",
                "r",
            )
            google = json.load(f)
        else:
            google = None
        if not email_preference.objects.filter(user_id=request.user).exists():
            meta_email = tmeta_email_preference.objects.all()
            for i in meta_email:
                email_preference.objects.create(
                    user_id=request.user, stage_id_id=i.id, is_active=i.is_active
                )
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_outlook.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json",
                "r",
            )
            outlook = json.load(f)
        else:
            outlook = None
        context = {
            "jd_id": pk,
            "applicant": applicant.values(),
            "shortlisted": shortlisted.values(),
            "interviewed": interviewed.values(),
            "selected": selected.values(),
            "rejected": rejected.values(),
            "params": params,
            "fav_id": fav_id,
            "google": google,
            "outlook": outlook,
            "total_applicants": applicants.filter(
                status_id__in=[1, 2, 3, 4, 7]
            ).count(),
        }
        return Response(context)


class matching_analysis(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)
        can_id = self.request.GET["can_id"]
        jd_id = self.request.GET["jd_id"]
        url = settings.gap_url
        headers = settings.xmp_headers
        try:
            match = Matched_candidates.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).values()
        except:
            match = None
        body = (
            """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/gap">
            <soapenv:Header/><soapenv:Body><xmp:analyse><action><left><index><index><caseType>job</caseType>
            <indexId>"""
            + user_id.username
            + """</indexId></index><caseId>"""
            + str(jd_id)
            + """</caseId></index></left><right>
            <index><index><caseType>candidate</caseType><indexId>"""
            + user_id.username
            + """</indexId></index><caseId>"""
            + str(can_id)
            + """</caseId>
            </index></right></action></xmp:analyse></soapenv:Body>
        </soapenv:Envelope>
        """
        )
        try:
            response = requests.post(url, data=body, headers=headers)
            data_dict = xmltodict.parse(response.content.decode("iso-8859-1"))
            json_data = json.dumps(data_dict)
            with open(base_dir + "/media/data-1.json", "w") as json_file:
                json_file.write(json_data)
                json_file.close()
            f = open(
                base_dir + "/media/data-1.json",
            )
            data = json.load(f)
            data = data["soap:Envelope"]["soap:Body"]["ns2:analyseResponse"]["return"]
            Matched_candidates.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).update(profile_match=round(float(data["score"]) * 100))
        except Exception as e:
            logger.error("Error in matching analysis, Error -- " + str(e))
            data = {}
        return Response({"success": True, "data": data, "match": match})


class MessagesAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chatname = self.request.GET["chatname"]
        jd_id = self.request.GET["jd_id"]
        users = User.objects.filter(id__in=chatname.split("-"))
        Message.objects.filter(jd_id_id=jd_id).exclude(sender=self.request.user).update(
            is_read=True
        )
        result = (
            Message.objects.filter(jd_id_id=jd_id)
            .filter(
                Q(sender=users[0], receiver=users[1])
                | Q(sender=users[1], receiver=users[0])
            )
            .annotate(
                username=F("sender__first_name"),
                last_name=F("sender__last_name"),
                message=F("text"),
                sender_image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("sender"))[:1].values(
                        "image"
                    )
                ),
                receiver_image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("receiver"))[:1].values(
                        "image"
                    )
                ),
            )
            .order_by("date_created")
            .values(
                "username",
                "last_name",
                "message",
                "sender",
                "receiver_image",
                "sender_image",
                "date_created",
            )
        )

        return JsonResponse(list(result), safe=False)


class candidate_notes(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pk = self.request.GET["pk"]
        result = Candidate_notes.objects.filter(candidate_id_id=pk)
        result = result.annotate(
            can_image=Subquery(
                Profile.objects.filter(
                    user_id=OuterRef("candidate_id__candidate_id__user_id")
                )[:1].values("image")
            ),
            emp_image=Subquery(
                Profile.objects.filter(user_id=OuterRef("client_id"))[:1].values(
                    "image"
                )
            ),
        )
        return Response(result.values())

    def post(self, request):
        if "update" in request.POST:
            notes = self.request.POST["notes"]
            pk = self.request.POST["pk"]
            Candidate_notes.objects.filter(
                id=pk,
            ).update(notes=self.request.POST["notes"], created_at=timezone.now())
            result = Candidate_notes.objects.filter(candidate_id_id=pk).values()
            return JsonResponse(list(result), safe=False)
        pk = self.request.GET["pk"]
        Candidate_notes.objects.create(
            client_id=self.request.user,
            candidate_id_id=pk,
            notes=self.request.POST["notes"],
            updated_by=str(self.request.user.first_name)
            + " "
            + str(self.request.user.last_name),
        )
        result = Candidate_notes.objects.filter(candidate_id_id=pk).values()
        return JsonResponse(list(result), safe=False)

    def delete(self, request):
        pk = self.request.GET["pk"]
        Candidate_notes.objects.filter(id=pk).delete()
        return JsonResponse({"success": True})


class Messages_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        result = tmeta_message_templates.objects.all().values()
        return JsonResponse(list(result), safe=False)


class messages_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        chatname = self.request.POST["chatname"]
        jd_id = self.request.POST["jd_id"]
        username = self.request.POST["username"]
        message = self.request.POST["message"]
        users = chatname.split("-")
        if self.request.user.is_staff:

            if company_details.objects.filter(recruiter_id=self.request.user).exists():
                sender = self.request.user
            else:
                sender = UserHasComapny.objects.get(user=self.request.user).company
                sender = sender.recruiter_id
            users.remove(str(sender.id))
            company_name = company_details.objects.get(recruiter_id=sender).company_name
        else:
            users.remove(str(self.request.user.id))
            sender = self.request.user
            company_name = sender.first_name

        receiver = User.objects.get(id=int(users[0]))
        Message(sender=sender, receiver=receiver, text=message, jd_id_id=jd_id).save()
        domain = settings.CLIENT_URL
        if self.request.user.is_staff:
            try:
                emp_can = employer_pool.objects.get(
                    client_id=self.request.user, email=receiver.email
                )
            except:
                emp_can = None

            if (
                applicants_status.objects.filter(candidate_id=emp_can, jd_id_id=jd_id)
                .exclude(status_id_id=6)
                .exists()
                == False
            ):
                Candi_invite_to_apply.objects.get_or_create(
                    client_id=self.request.user, candidate_id=emp_can, jd_id_id=jd_id
                )
            htmly = get_template("jobs/message.html")

            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
                receiver.email,
            )
            html_content = htmly.render(
                {
                    "sender": sender,
                    "receiver": receiver,
                    "jd_id": jd_id,
                    "company_name": company_name,
                    "message": message,
                    "domain": domain,
                    "date": timezone.now(),
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()

        else:
            htmly = get_template("jobs/message_staff.html")
            try:
                emp_can = employer_pool.objects.get(
                    client_id=receiver, email=sender.email
                )
            except:
                emp_can = None
            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
                receiver.email,
            )
            html_content = htmly.render(
                {
                    "sender": sender,
                    "receiver": receiver,
                    "jd_id": jd_id,
                    "company_name": company_name,
                    "message": message,
                    "domain": domain,
                    "date": timezone.now(),
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            data = "You got a message from " + str(sender.first_name.title())
            jd = JD_form.objects.get(id=jd_id)
            notify.send(
                receiver,
                recipient=receiver,
                description="messages",
                verb=data,
                target=emp_can,
                action_object=jd,
            )
        return Response(
            {
                "success": True,
            }
        )


class show_all_match(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pk = self.request.GET["pk"]
        user_id, updated_by = admin_account(self.request)
        jd_list = JD_form.objects.filter(
            user_id=user_id, jd_status_id__in=[1]
        ).values_list("id", flat=True)
        match = Matched_candidates.objects.filter(candidate_id_id=pk, jd_id__in=jd_list)
        applicant = applicants_status.objects.filter(
            candidate_id_id=pk, jd_id__in=jd_list, status_id__in=[1, 2, 3, 4, 7]
        )
        candidate_id = get_object_or_404(employer_pool, id=pk)
        fav = candidate_id.favourite.all()
        match = match.annotate(
            applicant=Subquery(
                applicant.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("id")
            ),
            invited=Subquery(
                Candi_invite_to_apply.objects.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("created_at")
            ),
            jd_title=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
            ),
            job_id=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_id")
            ),
            fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
        )
        applicant = applicant.annotate(
            invited=Subquery(
                Candi_invite_to_apply.objects.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("created_at")
            ),
            match=Subquery(
                match.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("profile_match")
            ),
            jd_title=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
            ),
            job_id=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_id")
            ),
            fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
        ).exclude(match__isnull=False)
        context = {
            "match": match.values(),
            "applicant": applicant.values(),
        }
        return Response(context)


class invite_to_apply(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        jd_id = self.request.POST["jd_id"]
        candidate_id = self.request.POST["candi_id"]
        user_id, updated_by = admin_account(self.request)
        if Candi_invite_to_apply.objects.filter(
            jd_id_id=jd_id,
            candidate_id_id=candidate_id,
            client_id=user_id,
        ).exists():
            Candi_invite_to_apply.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=candidate_id,
                client_id=user_id,
            ).update(created_at=timezone.now())
        else:
            Candi_invite_to_apply.objects.create(
                jd_id_id=jd_id,
                candidate_id_id=candidate_id,
                client_id=user_id,
            )
        candidate_details = employer_pool.objects.get(id=candidate_id)
        jd_id = JD_form.objects.get(id=jd_id)
        loc = JD_locations.objects.filter(jd_id=jd_id)
        qual = JD_qualification.objects.filter(jd_id=jd_id)
        detail = company_details.objects.filter(recruiter_id=user_id)
        try:
            match = Matched_candidates.objects.get(
                candidate_id=candidate_details, jd_id=jd_id
            ).profile_match
        except:
            match = None
        company_detail = company_details.objects.get(recruiter_id=user_id).company_name
        url = career_page_setting.objects.get(recruiter_id=user_id).career_page_url
        htmly = get_template("email_templates/invite_to_apply.html")
        current_site = settings.CLIENT_URL
        subject, from_email, to = (
            "Job Notification: An employer invitation to â€˜Apply for a Jobâ€™",
            email_main,
            candidate_details.email,
        )
        html_content = htmly.render(
            {
                "jd_id": jd_id,
                "url": url,
                "loc": loc,
                "match": match,
                "qual": qual,
                "detail": detail,
                "current_site": current_site,
                "company_detail": company_detail,
                "candidate_details": candidate_details,
                "job_pool": jd_id,
            }
        )
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = "related"
        msg.send()
        UserActivity.objects.create(
            user=self.request.user,
            action_id=5,
            action_detail='"'
            + str(candidate_details.first_name)
            + '" for the job id: '
            + str(jd_id.job_id),
        )

        data = {"success": True, "date": timezone.now().date().strftime("%b %d,  %Y")}
        return Response(data)


class applicant_status(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        try:
            jd_id = int(self.request.GET["jd_id"])
            can_id = int(self.request.GET["candi_id"])
            applied = applicants_screening_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=1
            ).values()
            shortlisted = applicants_screening_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[2]
            ).values()
            selected = applicants_screening_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[4]
            ).values()
            interviewed = applicants_screening_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[3]
            ).values()
            rejected = applicants_screening_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[7]
            ).values()
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).values()
            data = {
                "applied": applied,
                "shortlisted": shortlisted,
                "interviewed": interviewed,
                "selected": selected,
                "rejected": rejected,
                "invite": invite,
            }
            return Response(data)
        except Exception as e:
            logger.error("Error in applicant_status retrieve , Error -- " + str(e))
            return Response({"success": False})

    def post(self, request):

        try:
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["candi_id"]
            user_id, updated_by = admin_account(self.request)
            applicants_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=1
            ).update(status_id_id=2)
            applicants_screening_status.objects.get_or_create(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=2
            )
            time = timezone.now().strftime("%b %d,  %Y")
            return Response({"data": time, "success": True})
        except Exception as e:
            logger.error("Error in applicant_status update , Error -- " + str(e))
            return Response({"success": False})


class scorecard(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        try:
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["can_id"]
            rating = self.request.POST["rating"]
            comments = self.request.POST["comments"]
            if "rating" in self.request.POST:
                rating = rating
            else:
                rating = 0
            if interview_scorecard.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
            ).exists():
                interview_scorecard.objects.filter(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                ).update(rating=rating, comments=comments)
            else:
                interview_scorecard.objects.create(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                    rating=rating,
                    comments=comments,
                )
            interview = interview_scorecard.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
            ).values()

            return Response({"success": True, "interview": interview})
        except Exception as e:
            logger.error("Error in scorecard update , Error -- " + str(e))
            return Response({"success": False})

    def get(self, request):
        try:
            jd_id = self.request.GET["jd_id"]
            can_id = self.request.GET["can_id"]
            interview = interview_scorecard.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
            ).values()

            return Response({"interview": interview})

        except Exception as e:
            logger.error("Error in scorecard retrieve , Error -- " + str(e))
            return Response({"success": False})


class message_non_applicants(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        try:
            user_id, updated_by = admin_account(self.request)
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["can_id"]
            candidate_details = employer_pool.objects.filter(
                id=can_id, client_id=user_id
            )
            Message_non_applicants.objects.create(
                sender=user_id,
                receiver_id=can_id,
                jd_id_id=jd_id,
                text=self.request.POST["message"],
            )
            Candi_invite_to_apply.objects.get_or_create(
                jd_id_id=jd_id, candidate_id_id=can_id, client_id=user_id
            )
            candidate = employer_pool.objects.get(id=can_id).email
            htmly = get_template("jobs/Message_non_applicants.html")
            domain = settings.CLIENT_URL
            company_name = company_details.objects.get(
                recruiter_id=user_id
            ).company_name
            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
                candidate,
            )
            html_content = htmly.render(
                {
                    "sender": user_id,
                    "receiver": candidate_details[0],
                    "company_name": company_name,
                    "message": self.request.POST["message"],
                    "domain": domain,
                    "date": timezone.now(),
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            result = (
                Message_non_applicants.objects.filter(
                    sender_id=user_id.id, receiver_id=can_id, jd_id_id=jd_id
                )
                .annotate(
                    username=F("sender__first_name"),
                    message=F("text"),
                )
                .order_by("date_created")
                .values("username", "message", "sender", "date_created")
            )
            return JsonResponse(list(result), safe=False)
        except Exception as e:
            logger.error("Error in message non applicants update , Error -- " + str(e))
            return Response({"success": False})

    def get(
        self,
        request,
    ):
        try:
            user_id, updated_by = admin_account(self.request)
            jd_id = self.request.GET["jd_id"]
            can_id = self.request.GET["can_id"]
            result = (
                Message_non_applicants.objects.filter(
                    sender_id=user_id.id, receiver_id=can_id, jd_id_id=jd_id
                )
                .annotate(
                    username=F("sender__first_name"),
                    last_name=F("sender__last_name"),
                    message=F("text"),
                )
                .order_by("date_created")
                .values("username", "last_name", "message", "sender", "date_created")
            )
            return JsonResponse(list(result), safe=False)
        except Exception as e:
            logger.error(
                "Error in message non applicants retrieve , Error -- " + str(e)
            )
            return Response({"success": False})


class calender_event(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        try:
            can_id = self.request.GET["can_id"]
            candidate_details = employer_pool.objects.get(id=can_id)
            # google=google_return_details.objects.filter(client_id=self.request.user).values()
            # outlook = outlook_return_details.objects.filter(client_id=self.request.user).values()
            event = Event.objects.filter(
                user=self.request.user, attendees__icontains=candidate_details.email
            ).values()
            if os.path.exists(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json"
            ):
                f = open(
                    base_dir
                    + "/media/user_bin/"
                    + str(request.user.id)
                    + "_token_google.json",
                    "r",
                )
                google = json.load(f)
            else:
                google = []

            if os.path.exists(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json"
            ):
                f = open(
                    base_dir
                    + "/media/user_bin/"
                    + str(request.user.id)
                    + "_token_outlook.json",
                    "r",
                )
                outlook = json.load(f)
            else:
                outlook = []

            context = {
                "google": google,
                "event": event,
                "outlook": outlook,
            }

            return Response(context)
        except Exception as e:
            logger.error("Error in calender event retrieve , Error -- " + str(e))
            return Response({"success": False})


class applicants_pipline(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        try:
            has_permission = user_permission(self.request, "applicants")
            if not has_permission == True:
                permission = Permission.objects.filter(
                    user=self.request.user
                ).values_list("codename", flat=True)
                return Response({"success": True, "Permission": False})
            request = self.request
            pk = jd_id
            user_id, updated_by = admin_account(request)
            permission = Permission.objects.filter(user=request.user).values_list(
                "codename", flat=True
            )
            try:
                skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
            except:
                skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
            skill_list = json.load(skill_list)

            # result=matching_api_to_db(request,jd_id=pk,can_id=None)
            zita_match_count = zita_match_candidates.objects.filter(
                jd_id_id=pk,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
            ).count()
            job_details = JD_form.objects.filter(id=pk).annotate(
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country_id__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )

            context = {
                "success": True,
                "skill_list": skill_list,
                "zita_match_count": zita_match_count,
                "jd_id": pk,
                "job_details": job_details.values(
                    "country",
                    "job_title",
                    "job_role__label_name",
                    "job_id",
                    "state",
                    "city",
                )[0],
                "permission": permission,
            }
            return Response(context)
        except Exception as e:
            logger.error("Error in applicants pipline retrieve , Error -- " + str(e))
            return Response({"success": False})


class update_status(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        try:
            request = self.request
            pk = jd_id

            user_id, updated_by = admin_account(request)

            status = 1
            jd_id = JD_form.objects.get(id=pk)
            applicant_update = applicants_status.objects.get(
                id=request.GET["update_id"]
            )
            if request.GET["status"] == "new_applicants":
                status = 1
            elif request.GET["status"] == "shortlisted":
                status = 2
                UserActivity.objects.create(
                    user=request.user,
                    action_id=6,
                    action_detail='"'
                    + str(applicant_update.candidate_id.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            elif request.GET["status"] == "interviewed":
                status = 3
            elif request.GET["status"] == "offered":
                status = 4
                UserActivity.objects.create(
                    user=request.user,
                    action_id=7,
                    action_detail='"'
                    + str(applicant_update.candidate_id.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            elif request.GET["status"] == "rejected":
                status = 7
                UserActivity.objects.create(
                    user=request.user,
                    action_id=8,
                    action_detail='"'
                    + str(applicant_update.candidate_id.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            applicant_update.status_id_id = status
            applicant_update.updated_by = updated_by
            applicant_update.created_on = datetime.now()
            applicant_update.save()
            applicants_screening_status.objects.get_or_create(
                jd_id=jd_id,
                candidate_id=applicant_update.candidate_id,
                client_id=user_id,
                status_id_id=status,
                updated_by=updated_by,
            )
            return Response({"success": True})
        except Exception as e:
            logger.error(
                "Error in applicants update status api update , Error -- " + str(e)
            )
            return Response({"success": False})


class favourite(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        jd = self.request.GET["jd_id"]
        pk = self.request.GET["can_id"]
        jd_id = get_object_or_404(JD_form, id=jd)
        candidate_id = get_object_or_404(employer_pool, id=pk)

        data = {"success": False}
        if candidate_id.favourite.filter(id=jd_id.pk).exists():
            candidate_id.favourite.remove(jd_id)

        else:
            candidate_id.favourite.add(jd_id)
            data["success"] = True
        return JsonResponse(data)


class zita_match(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        has_permission = user_permission(self.request, "zita_match_candidate")
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})
        request = self.request
        pk = self.request.GET["jd_id"]
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        skill_list = json.load(skill_list)
        user = User.objects.get(username=request.user).id
        logger.info("In function shorlist_candidates - User ID: " + str(user))
        jd_state = JD_locations.objects.filter(jd_id_id=pk).values_list(
            "state_id", flat=True
        )
        job_details = (
            JD_form.objects.filter(id=pk)
            .annotate(
                profile=Subquery(
                    JD_profile.objects.filter(jd_id=OuterRef("id")).values(
                        "recommended_role_id__label_name"
                    )[:1]
                ),
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )
            .values(
                "country",
                "job_title",
                "job_id",
                "profile",
                "state",
                "city",
            )[0]
        )
        location = JD_locations.objects.filter(jd_id_id=pk).values_list(
            "state_id__name"
        )
        data = request.GET
        # matching_api_to_db(request, jd_id=pk,can_id=None)
        applicants_count = (
            applicants_status.objects.filter(jd_id_id=pk)
            .exclude(status_id_id=6)
            .count()
        )

        context = {
            "success": True,
            "skill_list": skill_list,
            "applicants_count": applicants_count,
            "jd_id": pk,
            "job_details": job_details,
        }
        return Response(context)


class zita_match_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):

        request = self.request
        pk = self.request.GET["jd_id"]
        user_id, updated_by = admin_account(request)
        user = User.objects.get(username=request.user).id
        logger.info("In function shorlist_candidates - User ID: " + str(user))
        data = request.GET
        get_dict_copy = request.GET.copy()
        fav_id = False
        zita_match = zita_match_candidates.objects.filter(
            jd_id_id=pk,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
        ).values_list("candidate_id", flat=True)
        data = employer_pool.objects.filter(id__in=zita_match)
        jd_list = get_object_or_404(JD_form, id=pk)
        fav = jd_list.favourite.all()
        data = data.annotate(
            fav=Subquery(fav.filter(id=OuterRef("id"))[:1].values("id")),
            applicant=Subquery(
                applicants_status.objects.filter(
                    jd_id_id=pk,
                    candidate_id=OuterRef("id"),
                    status_id__in=[1, 2, 3, 4, 7],
                )[:1].values("jd_id__job_title")
            ),
            match=Subquery(
                Matched_candidates.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )[:1].values("profile_match")
            ),
            image=Subquery(
                Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                    :1
                ].values("image")
            ),
            invite=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )[:1].values("created_at")
            ),
            applicant_view=Subquery(
                applicants_status.objects.filter(
                    client_id=user_id, candidate_id=OuterRef("id"), status_id_id=6
                )[:1].values("created_on")
            ),
            interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )
                .order_by("-created_at")[:1]
                .values("is_interested")
            ),
        ).order_by("-match")
        if "profile_match" in request.GET and len(request.GET["profile_match"]) > 0:
            try:
                if len(request.GET["profile_match"]) > 0:
                    data_profile = request.GET["profile_match"].split("-")
                    request.GET._mutable = True
                    request.GET["match_min"] = data_profile[0]
                    request.GET["match_max"] = data_profile[1]
                    data = data.filter(
                        match__range=(
                            request.GET["match_min"],
                            request.GET["match_max"],
                        )
                    )
            except:
                request.GET._mutable = True
                request.GET["profile_match"] = ""

        if "fav" in request.GET and len(request.GET["fav"]) > 0:

            if request.GET["fav"] == "add":
                fav_id = True
                data = data.exclude(fav__isnull=True)

        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                data = data.filter(email__icontains=request.GET["candidate"])
            else:
                data = data.filter(first_name__icontains=request.GET["candidate"])
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            if request.GET["work_experience"] == "0-1":
                data = data.filter(
                    work_exp__in=["0-1", "0", "Less than 1 year", "0-1 year"]
                )
            elif request.GET["work_experience"] == "10-30":
                data = data.filter(
                    work_exp__in=[
                        "More than 10 years",
                        "11",
                        "12",
                        "13",
                        "14",
                        "15",
                        "16",
                        "17",
                        "18",
                        "10+",
                    ]
                )
            elif request.GET["work_experience"] == "3-5":
                data = data.filter(work_exp__in=["3-5", "3", "4", "5", "3-5 years"])
            elif request.GET["work_experience"] == "1-2":
                data = data.filter(work_exp__in=["1-2", "1", "2", "1-2 years"])
            elif request.GET["work_experience"] == "6-10":
                data = data.filter(
                    work_exp__in=["6-10 years", "6-10", "6", "7", "8", "9", "10"]
                )
            else:
                data = data.filter(work_exp__icontains=request.GET["work_experience"])
        if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
            if request.GET["relocate"] == "1":
                data = data.filter(relocate=True)

        if "invite" in request.GET and len(request.GET["invite"]) > 0:
            if request.GET["invite"] == "1":
                data = data.exclude(invite__isnull=True)
            elif request.GET["invite"] == "0":
                data = data.exclude(invite__isnull=False)
        if "profile_view" in request.GET and len(request.GET["profile_view"]) > 0:
            if request.GET["profile_view"] == "1":
                data = data.exclude(applicant_view__isnull=True)
            elif request.GET["profile_view"] == "0":
                data = data.exclude(applicant_view__isnull=False)
        if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
            data = data.filter(job_type_id=request.GET["type_of_job"])
        if (
            "preferred_location" in request.GET
            and len(request.GET["preferred_location"]) > 0
        ):
            if request.GET["preferred_location"] == "1":
                location = JD_locations.objects.filter(jd_id_id=pk).values(
                    "state_id__name"
                )
                data = data.filter(
                    location__icontains=location.values("state_id__name")[0][
                        "state_id__name"
                    ]
                )
        if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
            data = data.filter(can_source_id=request.GET["user_type"])
            user_type = request.GET["user_type"]
        else:
            user_type = ""
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
                )
            )
        if "interested" in request.GET and len(request.GET["interested"]) > 0:
            if request.GET["interested"] == "interested":
                data = data.order_by("-interested")
            elif request.GET["interested"] == "not_interested":
                data = data.order_by("interested")
        total_count = data.count()
        page = request.GET.get("page", 1)
        paginator = Paginator(data, 20)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        get_dict_copy = request.GET.copy()
        del get_dict_copy["jd_id"]
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        context = {
            "data": data.object_list.values(),
            "jd_id": pk,
            "total_count": int(total_count),
            "fav_id": fav_id,
            "user_type": user_type,
            "params": params,
        }
        return Response(context)


class bulk_download(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        jd = request.POST["jd"]
        if "invite" in request.POST:
            for i in request.POST["candi_id"].split(","):
                Candi_invite_to_apply.objects.create(
                    jd_id_id=jd,
                    candidate_id_id=i,
                    client_id=user_id,
                )
                candidate_details = employer_pool.objects.get(id=i)
                jd_id = JD_form.objects.get(id=jd)
                loc = JD_locations.objects.filter(jd_id=jd_id)
                qual = JD_qualification.objects.filter(jd_id=jd_id)
                match = Matched_candidates.objects.filter(
                    candidate_id=candidate_details, jd_id=jd_id
                ).last()
                company_detail = company_details.objects.get(
                    recruiter_id=user_id
                ).company_name
                url = career_page_setting.objects.get(
                    recruiter_id=user_id
                ).career_page_url
                htmly = get_template("email_templates/invite_to_apply.html")
                current_site = get_current_site(request)
                subject, from_email, to = (
                    "Job Notification: An employer invitation to â€˜Apply for a Jobâ€™",
                    email_main,
                    candidate_details.email,
                )
                html_content = htmly.render(
                    {
                        "jd_id": jd_id,
                        "loc": loc,
                        "match": match,
                        "qual": qual,
                        "company_detail": company_detail,
                        "current_site": current_site,
                        "candidate_details": candidate_details,
                        "job_pool": jd_id,
                        "url": url,
                    }
                )
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.mixed_subtype = "related"
                msg.send()

                UserActivity.objects.create(
                    user=request.user,
                    action_id=5,
                    action_detail='"'
                    + str(candidate_details.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            data = {
                "success": True,
            }
        elif "download" in request.POST:
            domain = get_current_site(request)
            t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
            with zipfile.ZipFile(
                base_dir
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
                "w",
            ) as myzip:
                for i in request.POST["candi_id"].split(","):
                    try:
                        resume_file = (
                            candidate_parsed_details.objects.filter(candidate_id_id=i)
                            .first()
                            .resume_file_path
                        )
                        myzip.write(
                            base_dir + "/media/" + str(resume_file),
                            str(resume_file).split("/")[1],
                        )
                    except Exception as e:
                        pass
            myzip.close()
            file = open(
                base_dir
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
                "rb",
            )
            response = HttpResponse(file, content_type="application/zip")
            response["Content-Disposition"] = (
                "attachment; filename=candidates_profile_" + str(t) + ".zip"
            )
            data = {
                "success": True,
                "file_path": str(domain)
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
            }

        return Response(data)


class my_database(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        has_permission = user_permission(request, "my_database")
        if not has_permission == True:
            return Response({"success": True, "Permission": False})
        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        skill_list = json.load(skill_list)
        job_title = (
            JD_form.objects.filter(user_id=user_id, jd_status_id=1)
            .values("job_title", "id")
            .order_by("-job_posted_on")
        )

        try:
            candidate_available = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candidate_available = 0
        context = {
            "success": True,
            "job_title": job_title,
            "permission": permission,
            "skill_list": skill_list,
            "candidate_available": candidate_available,
        }
        return Response(context)


class my_database_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        fav_id = False
        user_id, updated_by = admin_account(request)
        data = (
            employer_pool.objects.filter(client_id=user_id)
            .order_by("-created_at")
            .exclude(email__isnull=True)
            .exclude(first_name__isnull=True)
        )
        data = data.annotate(
            applicant_view=Subquery(
                applicants_status.objects.filter(
                    client_id=user_id, candidate_id=OuterRef("id"), status_id_id=6
                )[:1].values("created_on")
            ),
            image=Subquery(
                Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                    :1
                ].values("image")
            ),
        ).order_by("-id")
        if "job_title" in request.GET and len(request.GET["job_title"]) > 0:
            jd = request.GET["job_title"]
            data = data.annotate(
                applicant=Subquery(
                    applicants_status.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )
                    .exclude(status_id_id=6)[:1]
                    .values("created_on")
                ),
                match=Subquery(
                    Matched_candidates.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )[:1].values("profile_match")
                ),
                invite=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )
                    .order_by("-created_at")[:1]
                    .values("created_at")
                ),
                interested=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )
                    .order_by("-created_at")[:1]
                    .values("is_interested")
                ),
                responded_date=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )[:1].values("responded_date")
                ),
            ).order_by("-match")
            if "fav" in request.GET and len(request.GET["fav"]) > 0:
                if request.GET["fav"] == "add":
                    fav_id = True
                    jd_list = get_object_or_404(JD_form, id=jd)
                    fav = jd_list.favourite.all()
                    data = data.annotate(
                        fav=Subquery(fav.filter(id=OuterRef("id"))[:1].values("id"))
                    ).exclude(fav__isnull=True)
        else:
            jd = False
            data = data.order_by("-id")
        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                data = data.filter(email__icontains=request.GET["candidate"])
            else:
                data = data.filter(first_name__icontains=request.GET["candidate"])
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            if request.GET["work_experience"] == "0-1":
                data = data.filter(
                    work_exp__in=["0-1", "0", "Less than 1 year", "0-1 year"]
                )
            elif request.GET["work_experience"] == "10+":

                data = data.filter(
                    work_exp__in=[
                        "More than 10 years",
                        "11",
                        "12",
                        "13",
                        "14",
                        "15",
                        "16",
                        "17",
                        "18",
                        "10+",
                    ]
                )

            elif request.GET["work_experience"] == "3-5":
                data = data.filter(work_exp__in=["3-5", "3", "4", "5", "3-5 years"])
            elif request.GET["work_experience"] == "1-2":
                data = data.filter(work_exp__in=["1-2", "1", "2", "1-2 years"])
            elif request.GET["work_experience"] == "6-10":
                data = data.filter(
                    work_exp__in=["6-10 years", "6-10", "6", "7", "8", "9", "10"]
                )

            else:
                data = data.filter(work_exp__icontains=request.GET["work_experience"])
        if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
            if request.GET["relocate"] == "1":
                data = data.filter(relocate=True)
        if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
            data = data.filter(job_type_id=request.GET["type_of_job"])
        if "location" in request.GET and len(request.GET["location"]) > 0:
            data = data.filter(location__icontains=request.GET["location"])
        if "user_type" in request.GET and len(request.GET["user_type"]) > 0:

            if (
                int(request.GET["user_type"]) == 3
                and request.GET["applicant_only"] == "1"
            ):

                data = data.filter(can_source_id=request.GET["user_type"]).exclude(
                    applicant__isnull=True
                )
            elif (
                int(request.GET["user_type"]) == 3
                and request.GET["applicant_only"] == "0"
            ):
                data = data.filter(can_source_id=request.GET["user_type"])
            else:
                data = data.filter(can_source_id=request.GET["user_type"])
            user_type = request.GET["user_type"]
        else:
            user_type = ""
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
                )
            )
        if "sort" in request.GET and len(request.GET["sort"]) > 0:
            if request.GET["sort"] == "interested":
                data = data.order_by("-interested", "-match")
            elif request.GET["sort"] == "not_interested":
                data = data.order_by("-responded_date", "interested", "-match")
            elif request.GET["sort"] == "name":
                data = data.order_by("first_name")
            elif request.GET["sort"] == "invited":
                data = data.order_by("-invite")
            elif request.GET["sort"] == "not_invited":
                data = data.order_by("invite")

        search = False
        total_count = data.count()
        try:
            if request.GET["search"] == "1":
                search = True
        except:
            pass
        page = request.GET.get("page", 1)
        paginator = Paginator(data, 20)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        data = data.object_list.values()
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        context = {
            "data": data,
            "jd": jd,
            "fav_id": fav_id,
            "total_count": total_count,
            "user_type": user_type,
            "params": params,
            "search": search,
        }
        return Response(context)


class company_detail(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        has_permission = user_permission(request, "manage_account_settings")
        if not has_permission == True:
            return Response({"success": True, "Permission": False})
        build_career_page = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        country = Country.objects.filter(name__in=countries_to_be_displayed)
        state = State.objects.filter(country_id__in=country)
        city = City.objects.filter(state_id__in=state)
        context = {
            "success": True,
            "build_career_page": build_career_page,
            "permission": permission,
            "country": country.values(),
            "state": state.values(),
            "city": city.values(),
            "company_detail": company_detail[0],
        }
        return Response(context)

    def post(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        recruiter = company_details.objects.get(recruiter_id=user_id)
        company_detail = company_details_form(
            request.POST, request.FILES, instance=recruiter
        )
        if company_detail.is_valid():
            temp = company_detail.save(commit=False)
            temp.recruiter_id = user_id
            temp.updated_by = updated_by
            main = temp.save()
            recruiter = company_details.objects.get(recruiter_id=user_id)
            UserDetail.objects.filter(user=user_id).update(
                contact=request.POST["contact"]
            )
            data = {"success": True}
            return Response(data)
        data = {"success": False}
        return Response(data)


class Password_Change(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request = self.request
        password = PasswordChangeForm(request.user, request.POST)
        if password.is_valid():
            user = password.save()
            update_session_auth_hash(request, user)
            data = {
                "success": True,
            }
            return Response(data)
        else:
            data = {"success": False, "msg": "Enter correct current password"}
        data = {
            "success": False,
        }
        return Response(data)


class user_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request.user
        user = User.objects.filter(id=self.request.user.id).values()
        profile = request.user.profile.image
        data = {"success": True, "user": user[0], "profile": str(profile)}
        return Response(data)

    def post(self, request, *args, **kwargs):
        request = self.request

        if "image_null" in request.POST:
            Profile.objects.filter(user=request.user)
            # Profile.objects.filter(user=request.user).update(image='default.jpg')

        # else:
        if "image" in request.POST:
            p_form = ProfileUpdateForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if p_form.is_valid():
                p_form.save()
                data = {"success": True}
        form = user_profile_form(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()

            data = {
                "success": True,
            }
        data = {
            "success": False,
        }
        return Response(data)


class build_career_page(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        has_permission = user_permission(request, "manage_account_settings")
        if not has_permission == True:
            return Response({"success": True, "Permission": False})
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        user_id, updated_by = admin_account(request)

        career_page_exists = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        if career_page_exists:
            career_page = career_page_setting.objects.filter(
                recruiter_id=user_id
            ).values()[0]
        else:
            career_page = None

        domain = settings.CLIENT_URL
        context = {
            "success": True,
            "career_page": career_page,
            "company_detail": company_detail[0],
            "career_page_exists": career_page_exists,
            "domain": str(domain),
            "permission": permission,
        }
        return Response(context)

    def post(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        career_page_exists = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        if not career_page_exists:
            setting_pages = career_page_setting_form(request.POST, request.FILES)
        else:
            setting_pages = career_page_setting_form(
                request.POST,
                request.FILES,
                instance=career_page_setting.objects.get(recruiter_id=user_id),
            )
        if setting_pages.is_valid():
            temp = setting_pages.save(commit=False)
            temp.recruiter_id = user_id
            temp.updated_by = updated_by
            temp.save()
            data = {"url": request.POST["career_page_url"], "success": True}
            return Response(data)
        data = {"success": False}
        return Response(data)


class career_page(generics.GenericAPIView):

    def get(self, request, url=None):
        request = self.request
        if request.GET["user_id"] != "0":
            login_user = True
        else:
            login_user = False
        try:
            user = career_page_setting.objects.get(career_page_url=url).recruiter_id
        except:
            user, updated_by = admin_account(request)
        jd_active = False

        if login_user:
            image = str(Profile.objects.get(user_id=int(request.GET["user_id"])).image)
            user_detail = User.objects.filter(id=int(request.GET["user_id"])).values()[
                0
            ]
        else:
            image = None
            user_detail = None

        jd_form = JD_form.objects.filter(user_id=user, jd_status_id=1)
        if jd_form.count() > 0:
            jd_active = True
        jd_form = jd_form.annotate(
            country=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "country__name"
                )
            ),
            state=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "state__name"
                )
            ),
            city=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "city__name"
                )
            ),
        ).order_by("-job_posted_on")
        jd_form = jd_form.annotate(
            job_location=Concat(
                "city",
                V(", "),
                "state",
                V(", "),
                "country",
                V("."),
                output_field=CharField(),
            )
        )
        filters = Career_filter(request.GET, queryset=jd_form)
        jd_form = filters.qs
        total = jd_form.count()
        try:
            company_detail = company_details.objects.filter(recruiter_id=user).values(
                "company_name",
                "company_website",
                "email",
                "address",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "logo",
            )
        except:
            company_detail = None
        # try:

        career_page_settings = career_page_setting.objects.filter(
            recruiter_id=user
        ).values()
        # except:
        # career_page_setting= None
        page = request.GET.get("page", 1)
        paginator = Paginator(jd_form, 10)

        try:
            jd_form = paginator.page(page)
        except PageNotAnInteger:
            jd_form = paginator.page(1)

        except EmptyPage:
            jd_form = paginator.page(paginator.num_pages)
        jd_form = jd_form.object_list.values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "job_location",
            "min_exp",
            "max_exp",
        )
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        context = {
            "jd_form": jd_form,
            "user_detail": user_detail,
            "params": params,
            "image": image,
            "total": total,
            "jd_active": jd_active,
            "login_user": login_user,
            "career_page_setting": career_page_settings[0],
            "company_detail": company_detail[0],
        }
        return Response(context)


class create_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)

        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        skill_list = json.load(skill_list)
        return Response({"data": data, "skill_list": skill_list, "success": True})

        # return Response({'data':data,})

    def post(
        self,
        request,
    ):
        request = self.request
        form = request.POST
        work_remote = True
        if form.get("work_remote") == "1":
            work_remote = True
        else:
            work_remote = False

        admin_id, updated_by = admin_account(self.request)
        jd = JD_form()
        jd.job_title = form["job_title"]
        jd.user_id = admin_id
        jd.job_role = tmeta_ds_main_roles.objects.get(id=int(form["job_role"]))
        jd.job_id = form["job_id"]
        jd.industry_type_id = form["industry_type"]
        jd.min_exp = form["min_exp"]
        if form["max_exp"] == "":
            jd.max_exp = None
        else:
            jd.max_exp = form["max_exp"]
        if form["no_of_vacancies"] == "":
            no_of_vacancies = None
        else:
            no_of_vacancies = form["no_of_vacancies"]
        jd.no_of_vacancies = no_of_vacancies
        jd.work_remote = work_remote
        jd.richtext_job_description = form["richtext_job_description"]
        text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        jd.job_description = text_des

        jd.salary_curr_type_id = int(form["salary_curr_type"])
        try:
            jd.show_sal_to_candidate = 1 if form["show_sal_to_candidate"] == "1" else 0
        except:
            pass
        if form["salary_min"] == "":
            jd.salary_min = None
        else:
            jd.salary_min = form["salary_min"]

        if form["salary_max"] == "":
            jd.salary_max = None
        else:
            jd.salary_max = form["salary_max"]
        jd.job_type_id = form["job_type"]
        jd.jd_status_id = int(2)
        jd.save()
        UserActivity.objects.get_or_create(
            user=request.user,
            action_id=1,
            action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
        )
        jd_id = JD_form.objects.filter(user_id=admin_id).last()

        qual_list = form["qualification"].split(",")
        spec_list = form["specialization"].split(",")
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )

        if form["job_role"] == "6" or form["job_role"] == 6:
            try:
                skills = form["skills"].split(",")
                for s in skills:
                    JD_skills_experience.objects.create(
                        skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
                    )
            except:
                pass
        else:
            mand_skill_list = form.getlist("skills")[0].split("|")
            skill_exp_list = form.getlist("skills_exp")[0].split(",")
            database_skill = form.getlist("database_skill")[0].upper().split(",")
            platform_skill = form.getlist("platform_skill")[0].upper().split(",")
            programming_skill = form.getlist("programming_skill")[0].upper().split(",")
            tool_skill = form.getlist("tool_skill")[0].upper().split(",")
            misc_skill = form.getlist("misc_skill")[0].upper().split(",")
            for s, e in zip(mand_skill_list, skill_exp_list):
                if s.upper() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                    )
                if s.upper() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                    )
                if s.upper() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                    )
                if s.upper() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                    )
                if s.upper() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                    )

        JD_locations.objects.create(
            country_id=int(form["work_country"]),
            state_id=int(form["work_state"]),
            city_id=int(form["work_city"]),
            jd_id_id=jd_id.id,
        )

        if "duplicate" in form and form["job_role"] != "6":
            profiler_input = [text_des]
            try:
                if profiler_input != []:
                    url = settings.profile_api_url
                    headers = {"Authorization": settings.profile_api_auth_token}
                    input_texts = profiler_input
                    texts_file = {"texts": "||".join(input_texts)}
                    result = requests.post(url, headers=headers, data=texts_file)
                    profiles = result.json()["profiles"]
                    profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                    profiles["data_analysis"] = profiles.pop("Data_Analysis")
                    profiles["data_eng"] = profiles.pop("Data_Engineering")
                    profiles["devops"] = profiles.pop("Dev_Ops")
                    profiles["ml_model"] = profiles.pop("Machine_Learning")
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = result.json()["recommended_roles"]
                    ds_profile = ""
                    if recommended_roles != []:
                        ds_profile = "DS Profile"
                    else:
                        ds_profile = "Others"
                        recommended_roles.append(ds_profile)
                    classification_url = settings.classification_url
                    cl_result = requests.post(
                        classification_url,
                        headers=headers,
                        data={"profiles": profiles.values()},
                    )

                    role_obj = tmeta_ds_main_roles.objects.get(
                        tag_name=recommended_roles[0].replace("_", " ")
                    )

                    JD_profile.objects.create(
                        jd_id=jd_id,
                        user_id=admin_id,
                        business_intelligence=profiles["bi_vis"],
                        data_analysis=profiles["data_analysis"],
                        data_engineering=profiles["data_eng"],
                        devops=profiles["devops"],
                        machine_learning=profiles["ml_model"],
                        others=profiles["others"],
                        recommended_role=role_obj,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )
            except Exception as e:
                logger.error("Profiling failed----" + str(e))

        context = {
            "success": True,
            "jd_id": jd_id.id,
        }
        return Response(context)


class edit_jd(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        request = self.request
        jd_id = pk
        user_id, updated_by = admin_account(request)
        edited_jd = request.POST

        text_des = re.sub(r"<.*?>", "", edited_jd["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        job_description = text_des
        if edited_jd["work_remote"] == "1":
            work_remote = True
        else:
            work_remote = False

        show_sal_to_candidate = (
            True if edited_jd.get("show_sal_to_candidate") == "1" else False
        )

        if edited_jd["max_exp"] == "":
            max_exp = None
        else:
            max_exp = edited_jd["max_exp"]
        if edited_jd["salary_min"] == "":
            salary_min = None
        else:
            salary_min = edited_jd["salary_min"]

        if edited_jd["salary_max"] == "":
            salary_max = None
        else:
            salary_max = edited_jd["salary_max"]
        if edited_jd["no_of_vacancies"] == "":
            no_of_vacancies = None
        else:
            no_of_vacancies = edited_jd["no_of_vacancies"]
        JD_locations.objects.filter(jd_id=jd_id).delete()
        JD_locations.objects.create(
            country_id=int(edited_jd["work_country"]),
            state_id=int(edited_jd["work_state"]),
            city_id=int(edited_jd["work_city"]),
            jd_id_id=jd_id,
        )
        qual_list = edited_jd["qualification"].split(",")
        spec_list = edited_jd["specialization"].split(",")
        JD_qualification.objects.filter(jd_id_id=jd_id).delete()
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id
            )

        if edited_jd["job_role"] == "6" or edited_jd["job_role"] == 6:

            skills = edited_jd["skills"].split(",")

            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            for s in skills:
                JD_skills_experience.objects.create(
                    skill=s, experience=0, jd_id_id=jd_id, category_id=5
                )
        else:
            mand_skill_list = edited_jd.getlist("skills")[0].split("|")
            skill_exp_list = edited_jd.getlist("skills_exp")[0].split(",")

            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            database_skill = edited_jd.getlist("database_skill")[0].upper().split(",")
            platform_skill = edited_jd.getlist("platform_skill")[0].upper().split(",")
            programming_skill = (
                edited_jd.getlist("programming_skill")[0].upper().split(",")
            )
            tool_skill = edited_jd.getlist("tool_skill")[0].upper().split(",")
            misc_skill = edited_jd.getlist("misc_skill")[0].upper().split(",")
            for s, e in zip(mand_skill_list, skill_exp_list):
                if s.upper() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=1
                    )
                if s.upper() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=2
                    )
                if s.upper() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=3
                    )
                if s.upper() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=4
                    )
                if s.upper() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=5
                    )

        JD_form.objects.filter(id=jd_id).update(
            job_title=edited_jd["job_title"],
            job_id=edited_jd["job_id"],
            no_of_vacancies=no_of_vacancies,
            industry_type_id=edited_jd["industry_type"],
            job_role=edited_jd["job_role"],
            min_exp=edited_jd["min_exp"],
            max_exp=max_exp,
            work_remote=work_remote,
            job_description=job_description,
            richtext_job_description=edited_jd["richtext_job_description"],
            salary_curr_type_id=edited_jd["salary_curr_type"],
            salary_min=salary_min,
            salary_max=salary_max,
            show_sal_to_candidate=show_sal_to_candidate,
            job_type=edited_jd["job_type"],
            updated_by=updated_by,
        )
        context = {"success": True, "jd_id": jd_id}
        return Response(context)


class dst_or_not(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        jd_id = pk
        request = self.request

        ds_role = JD_form.objects.get(id=jd_id).is_ds_role
        context = {
            "success": True,
            "ds_role": ds_role,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        jd_id = pk
        if request.POST["is_ds_role"] == "1":
            ds_role = True
        else:
            ds_role = False

        JD_form.objects.filter(id=jd_id).update(is_ds_role=ds_role)
        context = {
            "success": True,
            "ds_role": ds_role,
        }
        return Response(context)


# def validate_job_id(request):
class validate_job_id(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        job_id = request.GET.get("job_id", None)
        jd_id = request.GET.get("jd_id", None)
        data = {
            "is_taken": JD_form.objects.filter(user_id=user_id, job_id=job_id)
            .exclude(id=jd_id)
            .exists()
        }
        return Response(data)


class jd_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # if request.method=='POST':
        request = self.request

        jd_id = pk
        if request.POST.get("post_recom_role") is not None:
            role = request.POST.get("post_recom_role")
            logger.info("Recruiter has chosen recommended role ")
            role_obj = tmeta_ds_main_roles.objects.get(label_name=role)
            JD_form.objects.filter(id=jd_id).update(job_role_id=role_obj)
            JD_profile.objects.filter(jd_id_id=jd_id).update(role_acceptence=1)
            context = {
                "success": True,
                "new_role": role,
            }
            return Response(context)
        return Response(
            {
                "success": False,
                "old_role": request.POST["do_not_change"],
            }
        )

    def get(self, request, pk):
        request = self.request
        jd_id = pk
        admin_id, updated_by = admin_account(request)
        jd = JD_form.objects.get(id=jd_id)
        job_description = jd.job_description
        profiler_input = [job_description]
        try:
            if profiler_input != []:

                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = profiler_input
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                profiles = result.json()["profiles"]
                profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                profiles["data_analysis"] = profiles.pop("Data_Analysis")
                profiles["data_eng"] = profiles.pop("Data_Engineering")
                profiles["devops"] = profiles.pop("Dev_Ops")
                profiles["ml_model"] = profiles.pop("Machine_Learning")
                recommended_roles = result.json()["recommended_roles"]
                ds_profile = ""
                if recommended_roles != []:
                    ds_profile = "DS Profile"
                else:
                    ds_profile = "Others"
                    recommended_roles.append(ds_profile)
                classification_url = settings.classification_url
                cl_result = requests.post(
                    classification_url,
                    headers=headers,
                    data={"profiles": profiles.values()},
                )

                role_obj = tmeta_ds_main_roles.objects.get(
                    tag_name=recommended_roles[0].replace("_", " ")
                )
                JD_profile.objects.filter(
                    jd_id_id=jd_id,
                ).delete()
                JD_profile.objects.create(
                    jd_id_id=jd_id,
                    user_id=admin_id,
                    business_intelligence=profiles["bi_vis"],
                    data_analysis=profiles["data_analysis"],
                    data_engineering=profiles["data_eng"],
                    devops=profiles["devops"],
                    machine_learning=profiles["ml_model"],
                    others=profiles["others"],
                    recommended_role=role_obj,
                    dst_or_not=cl_result.json()["dst_or_not"],
                )

                profile_value = JD_profile.objects.filter(
                    jd_id_id=jd_id,
                ).values(
                    "business_intelligence",
                    "data_analysis",
                    "data_engineering",
                    "devops",
                    "machine_learning",
                    "others",
                    "recommended_role_id__label_name",
                )
            context = {
                "success": True,
                "profile_value": profile_value[0],
                "selected_role": jd.job_role.label_name,
            }
            return Response(context)
        except Exception as e:
            logger.error("Profiling failed----" + str(e))

        context = {
            "success": False,
        }
        return Response(context)


class jd_parser(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        request = self.request
        try:
            cd = clamd.ClamdUnixSocket()
            file = request.FILES["jd_file"]
            scan_results = cd.instream(file)
        except:
            scan_results = {"stream": ("OK", None)}

        if scan_results["stream"][0] == "OK":
            form_upload = Upload_jd(request.POST, request.FILES)
            if form_upload.is_valid():
                temp = form_upload.save(commit=False)
                temp.user_id = User.objects.get(username=request.user)
                temp.save()
                filepath = form_upload.instance.jd_file.path
                file_name = os.path.splitext(os.path.basename(filepath))
                filename = "".join(list(file_name))
                logger.info("Parsing the JD: " + str(filename))
            headers = {"Authorization": settings.jdp_api_auth_token}
            url = settings.jdp_api_url

            try:
                files = {
                    "jd_file": open(
                        os.getcwd() + "/" + "media/uploaded_jds/" + filename, "rb"
                    )
                }
            except:
                files = {
                    "jd_file": open(
                        base_dir + "/" + "media/uploaded_jds/" + filename, "rb"
                    )
                }
            result = requests.post(url, headers=headers, files=files)
            logger.debug("JD Parser API response " + str(result))
            parser_output = result.json()
            try:
                with open(
                    base_dir + "/" + "media/jd_output/" + filename + ".json", "w"
                ) as fp:
                    json.dump(parser_output, fp)
            except:
                with open(
                    os.getcwd() + "/" + "media/jd_output/" + filename + ".json", "w"
                ) as fp:
                    json.dump(parser_output, fp)
            qual_name = []
            role_and_res = []
            try:
                job_title = ", ".join(parser_output["job_title"])
            except:
                job_title = ""
            try:
                qual = parser_output["edu_qualification"]
                import re

                qual_list = re.split(", |_|-|!|\+", qual[0])
                for i in qual_list:
                    if i.lower().strip() in settings.ug:
                        qual_name.append({"qual": "Bachelors"})
                    if i.lower().strip() in settings.pg:
                        qual_name.append({"qual": "Masters"})
                    if i.lower().strip() in settings.phd:
                        qual_name.append({"qual": "Doctorate"})
            except KeyError:
                pass
            # [dict(t) for t in {tuple(d.items()) for d in l}]
            # result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in l)]
            try:
                add_in = parser_output["Additional Information"]

            except:
                pass

            try:
                roles = parser_output["roles_and_responsibilities"]
                role_and_res.append(
                    '<h6 style="font-weight:600">Roles and Responsibilities</h6>'
                )
                role_and_res.append("<br>".join(roles))
            except:
                pass

            try:
                tech_re = parser_output["Technical requirements"]
                role_and_res.append(
                    '<h6 style="font-weight:600;margin-top:1rem">Requirements</h6>'
                )
                role_and_res.append("<br>".join(tech_re))
            except:
                pass

            try:
                non_tech = parser_output["Non_Technical requirements"]
                role_and_res.append("<br>".join(non_tech))
            except:
                pass

            try:
                o_inf = parser_output["organisation_information"]
                if len(o_inf) > 0:
                    role_and_res.append(
                        '<h6 style="font-weight:600;margin-top:1rem">Organisation Information</h6>'
                    )
                    role_and_res.append("<br>".join(o_inf))
            except:
                pass

            try:
                add_in = parser_output["Additional Information"]
                if len(add_in) > 0:
                    role_and_res.append(
                        '<h6 style="font-weight:600;margin-top:1rem">Additional Information</h6>'
                    )
                    role_and_res.append("<br>".join(add_in))
            except:
                pass
            job_description = "".join(role_and_res)

            try:
                with open(base_dir + "/static/media/skills2.json", "r") as fp:
                    data = json.load(fp)
            except:
                with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                    data = json.load(fp)
            skills = parser_output["Skills"]["Mapped"]
            if "non_ds" in request.POST:
                skills_dic = []
                i = 1
                for skill in skills:
                    skills_dic.append({"skill": skill, "id": i, "exp": 0})
                    i = i + 1

                context = {
                    "success": True,
                    "qual_name": qual_name,
                    "skills": skills_dic,
                    "job_title": job_title,
                    "job_description": job_description,
                }
                return Response(context)

            tool = []
            database = []
            platform = []
            misc = []
            programming = []
            d = 1
            for prof in data:
                for i in data[prof]:
                    for skill in skills:
                        if skill.upper() in data[prof][i]:
                            if i == "tool":
                                tool.append({"skill": skill, "id": d, "exp": 0})
                            elif i == "database":
                                database.append({"skill": skill, "id": d, "exp": 0})
                            elif i == "platform":
                                platform.append({"skill": skill, "id": d, "exp": 0})
                            elif i == "programming":
                                programming.append({"skill": skill, "id": d, "exp": 0})
                            else:
                                misc.append({"skill": skill, "id": d, "exp": 0})
                            d = d + 1

            tool = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in tool)
            ]
            database = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in database)
            ]
            platform = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in platform)
            ]
            programming = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in programming)
            ]
            misc = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in misc)
            ]
            context = {
                "success": True,
                "qual_name": qual_name,
                "tool_skills": tool,
                "database_skills": database,
                "platform_skills": platform,
                "misc_skills": misc,
                "job_title": job_title,
                "programming_skills": programming,
                "job_description": job_description,
            }
        elif scan_results["stream"][0] == "FOUND":
            context = {"success": False, "error": "Virus found in submitted file"}

        return Response(context)


class duplicate(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request

        jd_id = pk
        jd = JD_form.objects.filter(id=jd_id).values()
        skills = JD_skills_experience.objects.filter(jd_id_id=jd_id).values()
        location = JD_locations.objects.filter(jd_id_id=jd_id).values()
        qualification = JD_qualification.objects.filter(jd_id_id=jd_id).values()
        jd_profile = JD_profile.objects.filter(jd_id_id=jd_id).exists()
        context = {
            "success": False,
            "jd_output": jd[0],
            "skills": skills,
            "location": location[0],
            "qualification": qualification,
            "jd_profile": jd_profile,
        }
        return Response(context)


class inactive_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        user_id, updated_by = admin_account(request)
        jd_id = pk

        JD_form.objects.filter(id=jd_id).update(jd_status_id=int(4))
        logger.info("In-activated JD successfully!!")
        jd_count = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=10
        )
        if jd_count.available_count != None:
            jd_count.available_count = jd_count.available_count + 1
            jd_count.save()
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=6, is_active=True
        ).exists():
            current_site = settings.CLIENT_URL
            mail_notification(
                user_id,
                "jd_inactive.html",
                "Job inactivated successfully ",
                jd_id=jd_id,
                domain=current_site,
                logo=True,
            )
        try:
            results = remove_case_id(request=request, can_id=None, jd_id=jd_id)
        except:
            pass
        return Response(
            {
                "success": True,
            }
        )


class post_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        jd_id = pk
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.get(id=jd_id)
        jd_count = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=10
        )
        if jd_count.available_count != None:
            if jd_count.available_count > 0:
                jd.job_posted_on = datetime.now()
                jd_count.available_count = jd_count.available_count - 1
                jd.jd_status_id = int(1)
                jd.save()
                UserActivity.objects.create(
                    user=request.user,
                    action_id=2,
                    action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
                )
                jd_count.save()
            else:
                jd_count.available_count = 0
                jd_count.save()
                data = {"success": False, "msg": "limit exists"}
                return Response(data)
        else:
            jd.job_posted_on = datetime.now()
            jd.jd_status_id = int(1)
            UserActivity.objects.create(
                user=request.user,
                action_id=2,
                action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
            )
            jd.save()
        result = generate_jd_json(request, pk=jd.id)
        logger.info("Posting JD " + str(jd))
        current_site = settings.CLIENT_URL
        import time

        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None
        time.sleep(2)
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=5, is_active=True
        ).exists():
            try:
                pass
                # result=matching_api_to_db(request,jd_id=pk,can_id=None)
            except Exception as e:
                logger.error("Error in the matching : " + str(e))
            jd_list = JD_form.objects.filter(id=pk)
            jd_list = jd_list.annotate(
                zita_match=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id_id=5,
                        candidate_id__first_name__isnull=False,
                        candidate_id__email__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("status_id")
                    .annotate(cout=Count("candidate_id"))[:1]
                    .values("cout"),
                    output_field=CharField(),
                ),
            )
            zita_match_candidate = zita_match_candidates.objects.filter(
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                jd_id=jd_list[0],
            )[:3]
            domain = settings.CLIENT_URL
            zita_match_candidate = zita_match_candidate.annotate(
                image=Subquery(
                    Profile.objects.filter(
                        user_id=OuterRef("candidate_id__candidate_id__user_id")
                    )[:1].values("image")
                ),
                match=Subquery(
                    Matched_candidates.objects.filter(
                        jd_id=OuterRef("jd_id"), candidate_id=OuterRef("candidate_id")
                    )[:1].values("profile_match")
                ),
            )
            career_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
            context = {
                "user": user_id,
                "jd_form": jd_list[0],
                "zita_match": zita_match_candidate,
                "career_url": career_url,
                "domain": domain,
            }
            email = get_template("email_templates/job_post_confirmation.html")
            email = email.render(context)
            msg = EmailMultiAlternatives(
                "Congratulations!!! Your job has been successfully posted on your career page",
                email,
                settings.EMAIL_HOST_USER,
                [user_id.email],
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
                "default.jpg",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            for p in zita_match_candidate:
                if p.image != None and p.image != "default.jpg":
                    msg.attach(profile(p.image))
            msg.mixed_subtype = "related"
            msg.send()
            # ur job has been successfully posted on your career page', jd_id=jd.id,count=0,domain=current_site)

        data = {
            "success": True,
            "url": str(current_site)
            + "/"
            + str(career_page_url)
            + "/career_job_view/"
            + str(jd.id)
            + "/"
            + str(jd.job_title),
        }
        return Response(data)


# class job_post_confirmation(generics.GenericAPIView):
# 	permission_classes = [
# 		permissions.IsAuthenticated
# 	]
# 	def get(self, request,pk):
# 		user_id,updated_by=admin_account(request)
# 		jd = JD_form.objects.get(id=pk)


class questionnaire_save(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        if "is_eeo_comp" in request.GET:
            if request.GET["is_eeo_comp"] == "1":
                eeo = True
            else:
                eeo = False
            JD_form.objects.filter(id=pk).update(is_eeo_comp=eeo)
            return Response({"success": True})

        JD_form.objects.filter(id=pk).update(jd_status_id=5)
        is_ds_role = False
        if not JD_form.objects.filter(id=pk, job_role_id=6).exists():
            is_ds_role = True
        context = {
            "pk": pk,
            "is_ds_role": is_ds_role,
            "applicant_qus": applicant_qus,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        if "temp" in request.POST:
            temp_list = request.POST["temp"].split(",")
            for i in temp_list:
                row_id = i.split("***")[0]
                row_req = i.split("***")[1]
                is_required = False
                if row_req == "true":
                    is_required = True
                template = applicant_questionnaire_template.objects.get(id=int(row_id))
                applicant_questionnaire.objects.create(
                    jd_id_id=pk,
                    field_type_id=template.field_type_id,
                    question=template.question,
                    description=template.description,
                    is_required=is_required,
                    option1=template.option1,
                    option2=template.option2,
                    option3=template.option3,
                    option4=template.option4,
                )
            context = {"success": True}
            return Response(context)
        if request.POST["required"] == "1":
            is_required = True
        else:
            is_required = False

        if (
            request.POST["field-type"] == "5"
            or request.POST["field-type"] == "6"
            or request.POST["field-type"] == "7"
        ):
            update_questionnaire = applicant_questionnaire.objects.create(
                jd_id_id=pk,
                field_type_id=int(request.POST["field-type"]),
                question=request.POST["question"],
                description=request.POST["description"],
                is_required=is_required,
            )
            option = request.POST.getlist("option")[0].split(",")
            for i in range(len(option)):
                if i == 0:
                    update_questionnaire.option1 = option[i]
                elif i == 1:
                    update_questionnaire.option2 = option[i]
                elif i == 2:
                    update_questionnaire.option3 = option[i]
                elif i == 3:
                    update_questionnaire.option4 = option[i]
            update_questionnaire.save()

        else:
            applicant_questionnaire.objects.create(
                jd_id_id=pk,
                field_type_id=int(request.POST["field-type"]),
                question=request.POST["question"],
                description=request.POST["description"],
                is_required=is_required,
            )
        context = {"success": True}
        return Response(context)

    def delete(self, request):
        applicant_questionnaire.objects.filter(
            id=int(self.request.GET["delete"])
        ).delete()
        context = {"success": True}
        return Response(context)


class questionnaire_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        template = applicant_questionnaire_template.objects.all().values()
        context = {
            "template": template,
        }
        return Response(context)


class questionnaire_for_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        user_id, updated_by = admin_account(request)
        if JD_form.objects.get(id=pk).jd_status.id != 6:
            JD_form.objects.filter(id=pk).update(jd_status_id=5)
        applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk).values()
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        country = JD_locations.objects.get(jd_id_id=pk).country.name
        is_eeo_comp = JD_form.objects.get(id=pk).is_eeo_comp

        context = {
            "company_name": company_name,
            "questionnaire_for_jd": applicant_qus,
            "is_eeo_comp": is_eeo_comp,
            "country": country,
        }
        return Response(context)

    def delete(self, request, pk):
        applicant_questionnaire.objects.filter(id=pk).delete()
        context = {"success": True}
        return Response(context)


class jd_preview(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        request = self.request

        status = JD_form.objects.get(id=pk)
        status.jd_status_id = 6
        status.save()
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
        )
        location = JD_locations.objects.filter(jd_id_id=pk).values(
            "country__name",
            "state__name",
            "city__name",
        )
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        qualification = JD_qualification.objects.filter(jd_id_id=pk).values()
        # profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
        try:
            profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
            recommended_role = JD_profile.objects.get(
                jd_id_id=pk
            ).recommended_role.label_name
        except:
            recommended_role = None
            profile = None
        try:
            plan_id = subscriptions.objects.get(
                is_active=True, client_id=user_id
            ).plan_id
            has_external_posting = plan_features.objects.filter(
                plan_id=plan_id, feature_id_id=13
            ).exists()
        except:
            has_external_posting = False
        try:
            available_jobs = client_features_balance.objects.get(
                feature_id_id=10, client_id=user_id
            ).available_count
        except:
            available_jobs = 0
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None

        context = {
            "jd": jd[0],
            "has_external_posting": has_external_posting,
            "available_jobs": available_jobs,
            "location": location[0],
            "skills": skills,
            "career_page_url": career_page_url,
            "qualification": qualification,
            "recommended_role": recommended_role,
            "profile": profile,
            "company_detail": company_detail[0],
        }
        return Response(context)


class jd_view(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        request = self.request

        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
        )
        location = JD_locations.objects.filter(jd_id_id=pk).values(
            "country__name",
            "state__name",
            "city__name",
        )
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        qualification = JD_qualification.objects.filter(jd_id_id=pk).values()
        try:
            profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
            recommended_role = JD_profile.objects.get(
                jd_id_id=pk
            ).recommended_role.label_name
        except:
            recommended_role = None
            profile = None
        try:
            plan_id = subscriptions.objects.get(
                is_active=True, client_id=user_id
            ).plan_id
            has_external_posting = plan_features.objects.filter(
                plan_id=plan_id, feature_id_id=13
            ).exists()
        except:
            has_external_posting = False
        try:
            available_jobs = client_features_balance.objects.get(
                feature_id_id=10, client_id=user_id
            ).available_count
        except:
            available_jobs = 0
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None
        int_list = {
            "posted_at": "",
            "reposted_on": "",
            "jd_status": "",
            "active_for": "",
            "zita_match": 0,
            "applicants": 0,
            "views": 0,
            "interviewed": 0,
            "screened": 0,
            "offered": 0,
        }
        final_list = []
        int_list["posted_at"] = JD_form.objects.get(id=pk).job_posted_on.date()
        try:
            active_for = (
                timezone.now().date() - JD_form.objects.get(id=pk).job_posted_on.date()
            )
            if active_for.days < 2:
                int_list["active_for"] = (
                    str(active_for.days)
                    + " day (Since "
                    + str(
                        JD_form.objects.get(id=pk)
                        .job_posted_on.date()
                        .strftime("%b %d, %Y")
                    )
                    + ")"
                )
            else:
                int_list["active_for"] = (
                    str(active_for.days)
                    + " days (Since "
                    + str(
                        JD_form.objects.get(id=pk)
                        .job_posted_on.date()
                        .strftime("%b %d, %Y")
                    )
                    + ")"
                )
        except:
            int_list["active_for"] = "NA"

        status_id = JD_form.objects.filter(id=pk).values("jd_status_id")[0][
            "jd_status_id"
        ]
        int_list["jd_status"] = tmeta_jd_status.objects.filter(id=status_id).values(
            "value"
        )[0]["value"]
        int_list["zita_match"] = zita_match_candidates.objects.filter(
            jd_id_id=pk,
            status_id_id=5,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
        ).count()
        int_list["applicants"] = applicants_status.objects.filter(
            jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
        ).count()
        int_list["shortlisted"] = (
            applicants_status.objects.filter(jd_id_id=pk, status_id_id__in=[2])
            .distinct()
            .count()
        )
        int_list["offered"] = (
            applicants_status.objects.filter(jd_id_id=pk, status_id_id=4)
            .distinct()
            .count()
        )
        int_list["invite"] = (
            Candi_invite_to_apply.objects.filter(jd_id_id=pk).distinct().count()
        )
        int_list["rejected"] = applicants_status.objects.filter(
            jd_id_id=pk, status_id_id=7
        ).count()
        job_count = (
            job_view_count.objects.filter(jd_id_id=pk)
            .values("source")
            .annotate(counts=Sum("count"))
            .aggregate(Sum("counts"))
        )

        if job_count["counts__sum"] == None:
            int_list["views"] = 0
        else:
            int_list["views"] = job_count["counts__sum"]
        role_base1 = []
        role_base2 = []
        data_dict = ["Applicants", "Views"]
        data_dict_ids = [1, 6]
        dates = list(
            sorted(
                set(
                    [
                        i["created_at"]
                        for i in job_view_count.objects.filter(jd_id_id=pk).values(
                            "created_at"
                        )
                    ]
                )
            )
        )
        date_list1 = list(
            job_view_count.objects.filter(jd_id_id=pk)
            .annotate(label=YearWeek("created_at"))
            .values("label")
            .annotate(y=Sum("count"))
        )
        date_list2 = list(
            applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
            )
            .annotate(label=YearWeek("created_on"))
            .values("label")
            .annotate(y=Count("id"))
        )
        posted_date = JD_form.objects.get(id=pk).job_posted_on
        posted_date = posted_date.strftime("%b-%d")
        date_list1.insert(0, {"label": posted_date, "y": 0})
        date_list2.insert(0, {"label": posted_date, "y": 0})
        role_base = [date_list1, date_list2]
        ext_jobs = external_jobpostings_by_client.objects.filter(
            jd_id_id=pk, is_active=True
        ).values()
        dates = 1
        if len(date_list1) == 1 and len(date_list2) == 1:
            dates = 0
        context = {
            "jd": jd[0],
            "has_external_posting": has_external_posting,
            "available_jobs": available_jobs,
            "location": location[0],
            "skills": skills,
            "dates": dates,
            "ext_jobs": ext_jobs,
            "career_page_url": career_page_url,
            "qualification": qualification,
            "recommended_role": recommended_role,
            "profile": profile,
            "job_view_line": date_list1,
            "applicants_line": date_list2,
            "int_list": int_list,
            "company_detail": company_detail[0],
        }
        return Response(context)


class job_view_count_fun(generics.GenericAPIView):

    def get(self, request, pk):

        source = request.GET["source"]

        if job_view_count.objects.filter(
            jd_id_id=pk, source=source, created_at=timezone.now().date()
        ).exists():
            job_view = job_view_count.objects.get(
                jd_id_id=pk, source=source, created_at=timezone.now().date()
            )
            job_view.count = job_view.count + 1
            job_view.save()
        else:
            job_view_count.objects.create(
                jd_id_id=pk, count=1, source=source, created_at=timezone.now().date()
            )

        return Response({"data": source})


class my_job_posting(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request

        admin_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        user = User.objects.get(username=request.user).id
        logger.info("In create_job_listing function - User ID: " + str(user))
        jd_list = JD_form.objects.filter(user_id=admin_id)
        jd_ids = jd_list.filter(jd_status_id=1).values_list("id", flat=True).distinct()
        for i in jd_ids:
            try:
                # result=matching_api_to_db(request,jd_id=i,can_id=None)
                pass
            except Exception as e:
                logger.error("Error in the matching : " + str(e))
        title = list(jd_list.values_list("job_title", flat=True).distinct())
        job_ids = list(jd_list.values_list("job_id", flat=True).distinct())
        location = JD_locations.objects.filter(
            jd_id__in=jd_list.values_list("id", flat=True).distinct()
        )
        location = location.annotate(
            countries=Subquery(
                Country.objects.filter(id=OuterRef("country"))[:1].values("name")
            ),
            states=Subquery(
                State.objects.filter(id=OuterRef("state"))[:1].values("name")
            ),
            cities=Subquery(
                City.objects.filter(id=OuterRef("city"))[:1].values("name")
            ),
        )
        location = location.annotate(
            loc=Concat(
                "cities",
                V(", "),
                "states",
                V(", "),
                "countries",
                output_field=CharField(),
            )
        )

        Jobs_List = 0
        if jd_list.exists():
            Jobs_List = 1

        location_list = list(
            location.values_list("loc", flat=True).exclude(loc__isnull=True).distinct()
        )
        job_title = list(jd_list.values_list("job_title", flat=True).distinct())

        context = {
            "location_list": location_list,
            "job_ids": job_ids,
            "job_title": job_title,
        }

        return Response(context)


class my_job_posting_data(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        user = User.objects.get(username=request.user).id
        logger.info("In create_job_listing function - User ID: " + str(user))
        admin_id, updated_by = admin_account(request)
        jd_list = JD_form.objects.filter(user_id=admin_id)
        jd_ids = jd_list.values_list("id", flat=True).distinct()
        location = JD_locations.objects.filter(
            jd_id__in=jd_list.values_list("id", flat=True).distinct()
        )
        location = location.annotate(
            countries=Subquery(
                Country.objects.filter(id=OuterRef("country"))[:1].values("name")
            ),
            states=Subquery(
                State.objects.filter(id=OuterRef("state"))[:1].values("name")
            ),
            cities=Subquery(
                City.objects.filter(id=OuterRef("city"))[:1].values("name")
            ),
        )
        location = location.annotate(
            loc=Concat(
                "cities",
                V(", "),
                "states",
                V(", "),
                "countries",
                output_field=CharField(),
            )
        ).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=admin_id
            ).career_page_url
        except:
            career_page_url = None

        Jobs_List = 1
        if jd_list.exists():
            Jobs_List = 2
        jd_list = jd_list.annotate(
            applicant=Subquery(
                applicants_status.objects.filter(
                    jd_id=OuterRef("id"), status_id_id__in=[1, 2, 3, 4, 7]
                )
                .values("client_id")
                .annotate(name=Count("id"))[:1]
                .values("name")
            ),
            selected=Subquery(
                applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=4)
                .values("client_id")
                .annotate(name=Count("id"))[:1]
                .values("name")
            ),
            rejected=Subquery(
                applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=7)
                .values("client_id")
                .annotate(name=Count("id"))[:1]
                .values("name")
            ),
            shortlisted=Subquery(
                applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=2)
                .values("client_id")
                .annotate(name=Count("id"))[:1]
                .values("name")
            ),
            location_jd=Subquery(
                location.filter(jd_id=OuterRef("id"))
                .values("jd_id")
                .annotate(name=Count("state"))
                .values("name")[:1]
            ),
            invite_to_apply=Subquery(
                Candi_invite_to_apply.objects.filter(jd_id=OuterRef("id"))
                .values("jd_id")
                .annotate(name=Count("candidate_id"))[:1]
                .values("name")
            ),
            interested=Subquery(
                jd_candidate_analytics.objects.filter(
                    jd_id=OuterRef("id"), status_id=5
                ).values("interested")[:1]
            ),
            location=Subquery(
                location.filter(jd_id=OuterRef("id"))
                .values("jd_id")
                .annotate(name=Concats("loc"))[:1]
                .values("name"),
                output_field=CharField(),
            ),
            job_posted_on_date=Case(
                When(job_reposted_on__isnull=False, then="job_reposted_on"),
                default=F("job_posted_on"),
            ),
        ).order_by("-job_posted_on_date")

        jd_list = jd_list.annotate(
            zita_match=Subquery(
                zita_match_candidates.objects.filter(
                    status_id_id=5,
                    candidate_id__first_name__isnull=False,
                    candidate_id__email__isnull=False,
                    jd_id=OuterRef("id"),
                )
                .values("status_id")
                .annotate(cout=Count("candidate_id"))[:1]
                .values("cout"),
                output_field=CharField(),
            ),
        )
        zita_count = []
        for jd_id in jd_ids:
            jd_states = JD_locations.objects.filter(jd_id=jd_id).values_list(
                "state_id", flat=True
            )
            cand_count = (
                zita_match_candidates.objects.filter(
                    status_id=5,
                    jd_id=jd_id,
                    candidate_id__first_name__isnull=False,
                    candidate_id__email__isnull=False,
                )
                .values("candidate_id")
                .distinct()
                .count()
            )
            zita_count.append((jd_id, cand_count))

        filters = JobFilter(request.GET, queryset=jd_list)
        final_list = filters.qs
        if "posted_on" in request.GET and request.GET["posted_on"] != "":
            date_posted = request.GET["posted_on"]
            today = timezone.now()
            date = today - timezone.timedelta(days=int(date_posted))
            final_list = final_list.filter(job_posted_on__range=(date, today))
        if "jd_status" in request.GET and request.GET["jd_status"] != "":
            status = request.GET["jd_status"].split(",")
            final_list = final_list.filter(jd_status_id__in=status)
        len_list = final_list.count()
        page = request.GET.get("page", 1)
        paginator = Paginator(final_list, 10)

        try:
            final_list = paginator.page(page)
        except PageNotAnInteger:
            final_list = paginator.page(1)

        except EmptyPage:
            final_list = paginator.page(paginator.num_pages)
        final_list = final_list.object_list.values(
            "applicant",
            "selected",
            "rejected",
            "id",
            "shortlisted",
            "invite_to_apply",
            "interested",
            "location",
            "job_posted_on_date",
            "job_title",
            "job_id",
            "is_ds_role",
            "job_type",
            "zita_match",
            "jd_status__label_name",
        )
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        domain = settings.CLIENT_URL
        context = {
            "final_list": final_list,
            "career_page_url": career_page_url,
            "len_list": len_list,
            "Jobs_List": Jobs_List,
            "params": params,
            "location": location,
            "zita_count": zita_count,
            "domain": domain,
        }
        return Response(context)


class dashboard(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        admin_id, updated_by = admin_account(request)
        try:
            company_name = Signup_Form.objects.get(user_id=admin_id).company_name
        except:
            company_name = "-"
        total_jobs = (
            JD_form.objects.filter(user_id=admin_id, jd_status_id__in=[1, 4])
            .values_list("id", flat=True)
            .distinct()
        )
        applicants = applicants_status.objects.filter(
            client_id=admin_id, status_id_id=1
        ).count()
        selected = applicants_status.objects.filter(
            client_id=admin_id, status_id=4
        ).count()
        job_count = (
            job_view_count.objects.filter(jd_id_id__in=total_jobs)
            .values("source")
            .annotate(count=Sum("count"))
            .order_by("-count")
        )
        viewed = employer_pool.objects.filter(
            client_id=admin_id, can_source_id=2
        ).count()
        rejected = applicants_status.objects.filter(
            client_id=admin_id, status_id=7
        ).count()
        invite_to_apply = Candi_invite_to_apply.objects.filter(
            client_id=admin_id
        ).count()
        shortlisted = applicants_status.objects.filter(
            client_id=admin_id, status_id__in=[2, 3]
        ).count()
        try:
            jobs_last_update = (
                JD_form.objects.filter(user_id=admin_id).last().created_on
            )
        except AttributeError:
            jobs_last_update = None
        try:
            applicants_last_update = (
                applicants_status.objects.filter(
                    client_id=admin_id, status_id__in=[1, 2, 3, 4, 7]
                )
                .last()
                .created_on
            )
        except AttributeError:
            applicants_last_update = None
        try:
            viewed_last_update = (
                employer_pool.objects.filter(client_id=admin_id, can_source_id=2)
                .last()
                .created_at
            )
        except AttributeError:
            viewed_last_update = None
        try:
            rejected_last_update = (
                applicants_status.objects.filter(client_id=admin_id, status_id=7)
                .last()
                .created_on
            )
        except AttributeError:
            rejected_last_update = None
        try:
            invite_to_apply_last_update = (
                Candi_invite_to_apply.objects.filter(client_id=admin_id)
                .last()
                .created_at
            )
        except AttributeError:
            invite_to_apply_last_update = None
        try:
            shortlisted_last_update = (
                applicants_status.objects.filter(
                    client_id=admin_id, status_id__in=[2, 3]
                )
                .last()
                .created_on
            )
        except AttributeError:
            shortlisted_last_update = None
        try:
            selected_last_update = (
                applicants_status.objects.filter(client_id=admin_id, status_id__in=[4])
                .last()
                .created_on
            )
        except AttributeError:
            selected_last_update = None
        jd_metrics = list(
            JD_form.objects.filter(user_id=admin_id, jd_status_id__in=[1, 4])
            .order_by("-job_posted_on")
            .values("id", "job_id", "job_title")
        )
        logo = company_details.objects.get(recruiter_id=admin_id).logo
        try:
            plan = subscriptions.objects.filter(client_id=admin_id).last()
            plan = subscriptions.objects.filter(subscription_id=plan.pk).values()[0]
        except:
            plan = None
        try:
            job_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=10
            ).available_count
        except:
            job_count = None
        try:
            contact_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=11
            ).available_count
        except:
            contact_count = None
        try:
            candidate_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=12
            ).available_count
        except:
            candidate_count = None
        total_count = Recommended_Role.objects.all().distinct().count()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=admin_id
            ).career_page_url
        except:
            career_page_url = ""
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_google.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json",
                "r",
            )
            google = json.load(f)
        else:
            google = None
        if not email_preference.objects.filter(user_id=request.user).exists():
            meta_email = tmeta_email_preference.objects.all()
            for i in meta_email:
                email_preference.objects.create(
                    user_id=request.user, stage_id_id=i.id, is_active=i.is_active
                )
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_outlook.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json",
                "r",
            )
            outlook = json.load(f)
        else:
            outlook = None
        domain = settings.CLIENT_URL
        user_info = User.objects.filter(id=request.user.id).values()[0]

        context = {
            "company_name": company_name,
            "total_jobs": len(total_jobs),
            "jobs_last_update": jobs_last_update,
            "applicants_last_update": applicants_last_update,
            "viewed_last_update": viewed_last_update,
            "outlook": outlook,
            "domain": domain,
            "career_page_url": career_page_url,
            "google": google,
            "logo": str(logo),
            "job_count": job_count,
            "user_info": user_info,
            "contact_count": contact_count,
            "candidate_count": candidate_count,
            "rejected_last_update": rejected_last_update,
            "invite_to_apply_last_update": invite_to_apply_last_update,
            "shortlisted_last_update": shortlisted_last_update,
            "selected_last_update": selected_last_update,
            "applicants": applicants,
            "shortlisted": shortlisted,
            "selected": selected,
            "viewed": viewed,
            "plan": plan,
            "rejected": rejected,
            "invite_to_apply": invite_to_apply,
            "jd_metrics": jd_metrics,
        }
        return Response(context)


class dashboard_calender(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        events = Event.objects.filter(user=request.user)

        if "date" in request.GET and request.GET["date"] != "":
            end_date = datetime.strptime(request.GET["date"], "%Y-%m-%d")
            end_time = end_date + timezone.timedelta(days=1)
            events = events.filter(
                user=request.user, start_time__range=(end_date, end_time)
            ).order_by("start_time")

        context = {
            "events": events.values(),
        }
        return Response(context)


class dashboard_message(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        admin_id, updated_by = admin_account(request)
        message = Message.objects.filter(receiver=admin_id, is_read=False)
        message = message.values_list("sender", "jd_id").distinct()
        message = message.annotate(
            first_name=Subquery(
                User.objects.filter(id=OuterRef("sender")).values("first_name")[:1]
            ),
            last_name=Subquery(
                User.objects.filter(id=OuterRef("sender")).values("last_name")[:1]
            ),
            jd=Subquery(JD_form.objects.filter(id=OuterRef("jd_id")).values("id")[:1]),
            message=Subquery(
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
                .values("text")
                .order_by("-date_created")[:1]
            ),
            is_read=Subquery(
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
                .values("is_read")
                .order_by("-date_created")[:1]
            ),
            time=Subquery(
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
                .values("date_created")
                .order_by("-date_created")[:1]
            ),
            profile_pic=Subquery(
                Profile.objects.filter(user=OuterRef("sender"))[:1].values("image")
            ),
            can_id=Subquery(
                employer_pool.objects.filter(candidate_id__user_id=OuterRef("sender"))[
                    :1
                ].values("id")
            ),
            can_source=Subquery(
                employer_pool.objects.filter(candidate_id__user_id=OuterRef("sender"))[
                    :1
                ].values("can_source__value")
            ),
        ).values()

        message_count = len(message)
        context = {
            "message": message,
            "message_count": message_count,
        }
        return Response(context)


def pie_chart(request, prof, filename):
    prof = prof[0]
    r = dict(prof)
    for k, v in prof.items():
        if v == "0.0" or v == "0":
            del r[k]
        else:
            r[k] = str(round(int(float(v))))

    label = list(r.keys())
    data = list(r.values())

    role_inverse_dict = {
        "data_analysis": "Data Analyst",
        "business_intelligence": "Business Intelligence",
        "machine_learning": "Machine Learning\nEngineer",
        "devops": "Devops Engineer",
        "data_engineering": "Big Data\nEngineer",
        "others": "Others",
    }
    textprops = {"fontsize": 15}
    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect="equal"))
    # slices = sorted(data)
    # small = slices[len(int(slices)) / 2:]
    # large = slices[:len(int(slices)) / 2]
    # reordered = large[::2] + small[::2] + large[1::2] + small[1::2]
    # angle = 180 + float(sum(small[::2])) / sum(reordered) * 360
    colors = [
        "#ff63849c",
        "#4bc0c09c",
        "#ffcd569c",
        "#ff9f409c",
        "#36a2eb9c",
        "#73eb369c",
    ]
    wedges, texts = ax.pie(
        data,
        labeldistance=1.05,
        wedgeprops={"alpha": 0.7},
        colors=colors,
        startangle=70,
    )

    # import math
    # for labels, t in zip(label, texts):
    #     x, y = t.get_position()
    #     angle = int(math.degrees(math.atan2(y, x)))
    #     ha = "left"

    #     if x<0:
    #         angle -= 180
    #         ha = "right"

    #     plt.annotate(labels, xy=(x,y), rotation=angle, ha=ha, va="center", rotation_mode="anchor", size=6)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), zorder=0, va="center")
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(
            role_inverse_dict[label[i]] + "-" + data[i] + "%",
            rotation_mode="anchor",
            xy=(x, y),
            xytext=(1.35 * np.sign(x), 1.4 * y),
            horizontalalignment=horizontalalignment,
            **kw
        )

    plt.savefig(
        base_dir + "/media/charts/pie_" + str(filename) + ".png", bbox_inches="tight"
    )
    plt.close()
    return


class download_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        pk = request.GET["jd_id"]
        jd_form = JD_form.objects.get(id=pk)
        skill = JD_skills_experience.objects.filter(jd_id_id=pk)
        location = JD_locations.objects.filter(jd_id_id=pk)
        location = [
            (
                City.objects.filter(id=i["city"]).values("name")[0]["name"],
                State.objects.filter(id=i["state"]).values("name")[0]["name"],
                Country.objects.filter(id=i["country"]).values("name")[0]["name"],
            )
            for i in JD_locations.objects.filter(jd_id_id=pk).values(
                "country", "state", "city"
            )
        ]

        education = [
            (i["qualification"], i["specialization"])
            for i in JD_qualification.objects.filter(jd_id_id=pk).values(
                "qualification", "specialization"
            )
        ]

        prof = list(
            JD_profile.objects.filter(jd_id_id=pk).values(
                "business_intelligence",
                "data_analysis",
                "data_engineering",
                "devops",
                "machine_learning",
                "others",
            )
        )
        if len(prof) > 0:
            try:
                pie_chart(request, prof, filename="jd_" + str(pk))
                is_profiled = 1
            except IndexError:
                is_profiled = 0
        else:
            is_profiled = 0
        params = {
            "jd_form": jd_form,
            "skill": skill,
            "location": location,
            "education": education,
            "is_profiled": is_profiled,
        }

        html_template = (
            get_template("pdf/jd_download.html").render(params).encode(encoding="UTF-8")
        )
        pdf_file = HTML(
            string=html_template, base_url=settings.profile_pdf_url
        ).write_pdf()
        f = open(base_dir + "/media/jd_" + str(jd_form.job_id) + ".pdf", "wb")
        f.write(pdf_file)
        domain = request.build_absolute_uri("/")
        return JsonResponse(
            {"file_path": str(domain) + "media/jd_" + str(jd_form.job_id) + ".pdf"}
        )


from jobs.candidate_data import get_app_prof_details


def assessment_data(request, id):
    user = User_Info.objects.get(application_id_id=id)
    recom_role = Recommended_Role.objects.filter(application_id_id=id)
    user_id = user.user_id_id
    main_prof_dict = {}
    main_claimed_prof = {}
    evaluation = {}
    avg_score = {}
    usecase_success = []
    recommended_role_list = []
    dset_status = 0
    for r in recom_role:
        ds_main_roles = r.recommended_role.id
        recommended_role_list.append(r.recommended_role.label_name)
        if Test_Assign.objects.filter(
            user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
        ).exists():
            dset_status = 1
            dset_status = Test_Assign.objects.get(
                user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
            ).dset_status.id
            claimed_prof_status = (
                1
                if Tech_proficiency.objects.filter(
                    application_id_id__user_id_id=user_id,
                    role_id_id=ds_main_roles,
                    active_test=1,
                ).exists()
                else 0
            )
            # selected_role=r
            # claimed_prof = {i['Skill'].lower():i['level'] for i in Tech_proficiency.objects.filter(application_id_id__user_id_id=user_id, role_id_id=ds_main_roles,active_test=1).values('Skill','level')}
            if dset_status == 5:
                distinct_secs = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values("section__label_name")
                    .distinct()
                )
                test_obj = Test_Assign.objects.get(
                    user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                )
                parameters = Create_test.objects.get(test_id=test_obj.test_id_id)

                ### for table summary
                summary_results = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values(
                        "section__label_name",
                        "question_id_id__difficulty_level__label_name",
                    )
                    .order_by("section__label_name")
                    .annotate(
                        total=Count("marks"),
                        correct=Sum("marks"),
                        percent=Sum("marks") / Count("marks") * 100,
                    )
                )

                order = []
                order = [
                    i[0]
                    for i in tmeta_difficulty_level.objects.values_list(
                        "label_name", flat=0
                    )
                ]
                order = {key: i for i, key in enumerate(order)}
                ordered_sections = sorted(
                    summary_results,
                    key=lambda i: (
                        i["section__label_name"],
                        order.get(i["question_id_id__difficulty_level__label_name"], 0),
                    ),
                )
                section_arr_table = [list(os.values()) for os in summary_results]

                ### for prof_ex
                prof_res = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values("section__label_name")
                    .order_by("section__label_name")
                    .exclude(question_id_id__question_type=2)
                    .annotate(
                        easy_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=1)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=1))
                        * 100,
                        med_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=2)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=2))
                        * 100,
                        hard_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=3)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=3))
                        * 100,
                    )
                )

                prof_dict = {}
                for section_dict in prof_res:
                    sec_name = section_dict["section__label_name"]
                    prof_level = 1
                    if section_dict["easy_percent"]:
                        if section_dict["easy_percent"] > 60:
                            prof_level = 2
                    if section_dict["med_percent"]:
                        if section_dict["med_percent"] > 60:
                            prof_level = 3
                    if section_dict["hard_percent"]:
                        if section_dict["hard_percent"] > 60:
                            prof_level = 4

                    prof_dict[sec_name.capitalize()] = prof_level
                if parameters.is_coding:
                    for i in range(len(section_arr_table)):
                        if section_arr_table[i][0] == "coding":
                            code_prof = section_arr_table[i][4]
                        else:
                            code_prof = 1

                    if code_prof == 0:
                        code_level = 1
                    elif code_prof == 50:
                        code_level = 3
                    elif code_prof == 100:
                        code_level = 4
                    else:
                        code_level = 1

                    prof_dict.update({"Coding": code_level})
                created_on = Test_Assign.objects.get(
                    user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                ).created_on.strftime(" %b %d, %Y")
                prof_dict.update({"dset_date": created_on})

                if Sloved_Usecase.objects.filter(
                    upload_id_id__user_id_id=user_id,
                    role_id_id=ds_main_roles,
                    active_test=1,
                ).exists():
                    usecase_date = Sloved_Usecase.objects.get(
                        upload_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).updated_at.strftime(" %b %d, %Y")

                    prof_dict.update({"usecase_date": usecase_date})
                else:
                    prof_dict.update({"usecase_date": 0})
            else:
                prof_dict = 0

        else:

            prof_dict = 0

        main_prof_dict.update({r.recommended_role.label_name: prof_dict})

        try:
            usecase = Usecase.objects.get(
                application_id_id__user_id_id=user_id,
                role_id_id=ds_main_roles,
                active_test=1,
            )
        except:
            usecase = None

        if Usecase_evaluation.objects.filter(usecase_id=usecase).exists():
            usecase_status = 1
            evaluation_list = Usecase_evaluation.objects.filter(
                usecase_id=usecase
            ).values()
            evaluation_list = evaluation_list.annotate(
                metric_value=Subquery(
                    tmeta_metric_score.objects.filter(id=OuterRef("metric_id"))[
                        :1
                    ].values("value")
                ),
            ).order_by("-metric_id")
            avg_score_list = list(
                avg_metrics_score.objects.filter(
                    role_id_id=r.recommended_role.id
                ).values()
            )
            evaluation.update(
                {r.recommended_role.label_name: list(evaluation_list.values())}
            )
            avg_score.update({r.recommended_role.label_name: list(avg_score_list)})

        else:
            usecase_status = 0

    return main_prof_dict, evaluation, avg_score, dset_status, recommended_role_list


class download_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jd = None
        request = self.request
        pk = request.GET["can_id"]

        user_id = Personal_Info.objects.get(application_id=pk).user_id_id
        view_contact = False
        if jd != None:
            # Skill match
            # jd = page_id
            jd_obj = JD_form.objects.get(id=jd)
            is_applicant = jd_candidate_analytics.objects.filter(
                candidate_id_id=pk, status_id_id=int(1), jd_id_id=jd
            ).exists()
            jd_skills = [
                i[0]
                for i in JD_skills_experience.objects.filter(jd_id_id=jd).values_list(
                    "skill"
                )
            ]
            skill_list = list(set(flatten(jd_skills)))
            skill_match = JD_form.objects.filter(id=jd).values("id")
            matched_cand = Matched_candidates.objects.filter(
                application_id=pk, jd_list_id_id__zita_jd_id_id=jd
            )
            skill_match = skill_match.annotate(
                skill_match=Subquery(
                    matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                        "skill_match"
                    )
                ),
                profile_match=Subquery(
                    matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                        "profile_match"
                    )
                ),
            )
            # if request.user.is_staff:
            view_contact = jd_candidate_analytics.objects.filter(
                candidate_id_id=pk,
                status_id_id=int(17),
                jd_id_id=jd,
                recruiter_id=request.user,
            ).exists()
            # else:
            # 	view_contact = False
            user, resume_details, prof = get_app_prof_details(
                u_id=user_id, for_exp=True, jd_id=jd, epf=True
            )

        else:
            skill_match = 0
            role_match = 0
            skill_list = 0
            jd_obj = 0
            is_applicant = 1
            if "page" in request.GET:
                if request.GET["page"] == "cpf":
                    user, resume_details, prof = get_app_prof_details(
                        u_id=user_id, for_exp=True, jd_id=None, epf=False
                    )
                    is_applicant = 1
                else:
                    user, resume_details, prof = get_app_prof_details(
                        u_id=user_id,
                        for_exp=True,
                        jd_id=None,
                        epf=False,
                        user_id=request.user,
                    )
            else:
                user, resume_details, prof = get_app_prof_details(
                    u_id=user_id, for_exp=True, jd_id=None, epf=False
                )
        current_site = get_current_site(request)
        personal = Personal_Info.objects.get(user_id=user_id)

        try:
            is_profiled = 1
            pie_chart(request, prof, filename=str(user_id))
        except IndexError:
            is_profiled = 0

        role_match = 0
        if skill_match != 0:
            if skill_match[0]["profile_match"] != None:
                role_match = skill_match[0]["profile_match"]
                name_file = str(user_id) + str(jd)
                venn_diagram(
                    request, match=skill_match[0]["profile_match"], filename=name_file
                )

        main_prof_dict, evaluation, avg_score, dset_status, recommended_role_list = (
            assessment_data(request, user.application_id)
        )
        for r in main_prof_dict:
            if main_prof_dict[r] != 0:
                area_chart(
                    request,
                    main_prof_dict[r],
                    filename="chart_" + str(r) + str(user_id),
                )
        for eva in evaluation:
            if evaluation[eva] != 0:
                redar_chart(
                    request,
                    evaluation[eva],
                    avg_score[eva],
                    filename="chart_" + eva + str(user_id),
                )
        if skill_match != 0:
            if skill_match[0]["profile_match"] != None:
                your_match = skill_match[0]["skill_match"].split(",")
                non_match = [e for e in skill_list if e not in your_match]
            else:
                your_match = None
                non_match = None
        else:
            your_match = None
            non_match = None
        media = settings.MEDIA_ROOT
        params = {
            "object": resume_details,
            "is_profiled": is_profiled,
            "recommended_role_list": (" / ").join(recommended_role_list),
            "user": user,
            "domain": current_site.domain,
            "request": request,
            "personal": personal,
            "role_match": role_match,
            "main_prof_dict": main_prof_dict,
            "skill_list": skill_list,
            "your_match": your_match,
            "non_match": non_match,
            "evaluation": evaluation,
            "jd_obj": jd_obj,
            "is_applicant": is_applicant,
            "view_contact": view_contact,
            "dset_status": dset_status,
            "media": media,
        }

        html_template = (
            get_template("pdf/candidate_profile.html")
            .render(params)
            .encode(encoding="UTF-8")
        )
        # pdf_file = HTML(string=html_template,base_url=request.build_absolute_uri()).write_pdf()
        pdf_file = HTML(
            string=html_template, base_url=settings.profile_pdf_url
        ).write_pdf()

        f = open(base_dir + "/media/Profile.pdf", "wb")
        f.write(pdf_file)
        domain = get_current_site(request)
        return JsonResponse({"file_path": str(domain) + "/media/Profile.pdf"})


class dashboard_job_metrics(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        pk = request.GET["jd_id"]
        # pk=101
        job_count = (
            job_view_count.objects.filter(jd_id_id=pk)
            .values("source")
            .annotate(count=Sum("count"))
            .order_by("-count")
        )
        total_count = job_count.aggregate(Sum("count"))
        role_base1 = []
        role_base2 = []
        posted_channel = external_jobpostings_by_client.objects.filter(
            jd_id_id=pk
        ).count()
        dates = list(
            sorted(
                set(
                    [
                        i["created_at"]
                        for i in job_view_count.objects.filter(jd_id_id=pk).values(
                            "created_at"
                        )
                    ]
                )
            )
        )
        date_list1 = list(
            job_view_count.objects.filter(jd_id_id=pk)
            .annotate(label=YearWeek("created_at"))
            .values("label")
            .annotate(y=Sum("count"))
        )
        date_list2 = list(
            applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
            )
            .annotate(label=YearWeek("created_on"))
            .values("label")
            .annotate(y=Count("id"))
        )
        posted_date = JD_form.objects.get(id=pk).job_posted_on
        posted_date = posted_date.strftime("%b-%d")
        date_list1.insert(0, {"label": posted_date, "y": 0})
        date_list2.insert(0, {"label": posted_date, "y": 0})
        role_base = [date_list1, date_list2]
        pipeline = []
        pipeline.append({"Views": total_count["count__sum"]})
        pipeline.append(
            {
                "Applicants": applicants_status.objects.filter(
                    jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
                ).count()
            }
        )
        pipeline.append(
            {
                "Shortlisted": applicants_status.objects.filter(
                    jd_id_id=pk, status_id_id__in=[2]
                ).count()
            }
        )
        pipeline.append(
            {
                "Offered": applicants_status.objects.filter(
                    jd_id_id=pk, status_id_id__in=[4]
                ).count()
            }
        )
        pipeline.append(
            {
                "Rejected": applicants_status.objects.filter(
                    jd_id_id=pk, status_id_id__in=[7]
                ).count()
            }
        )

        total_invite = list(
            Candi_invite_to_apply.objects.filter(jd_id_id=pk)
            .values_list("candidate_id", flat=True)
            .distinct()
        )
        my_database = []
        job_details = (
            JD_form.objects.filter(id=pk)
            .annotate(
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country_id__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )
            .values()
        )
        zita_match = zita_match_candidates.objects.filter(jd_id_id=pk).count()
        my_database.append(
            {"Zita Match": zita_match_candidates.objects.filter(jd_id_id=pk).count()}
        )
        my_database.append(
            {
                "Invited to Apply": Candi_invite_to_apply.objects.filter(
                    jd_id_id=pk
                ).count()
            }
        )
        my_database.append(
            {
                "Applicant Conversion": applicants_status.objects.filter(
                    jd_id_id=pk,
                    candidate_id__in=total_invite,
                    status_id_id__in=[1, 2, 3, 4, 7],
                ).count()
            }
        )
        applicant_count = (
            applicants_status.objects.filter(jd_id_id=pk, status_id__in=[1, 2, 3, 4, 7])
            .exclude(source__isnull=True)
            .values("source")
            .annotate(count=Count("candidate_id"))
        )
        total_count = applicant_count.aggregate(Sum("count"))

        perc_dict = []
        for i in applicant_count:

            perc = (int(i["count"]) / total_count["count__sum"]) * 100
            perc_dict.append({i["source"]: "{:.2f}".format(perc)})

        context = {
            "role_base": role_base,
            "posted_date": posted_date,
            "dates_length": dates,
            "zita_match": zita_match,
            "posted_channel": posted_channel,
            "total_count": total_count,
            "job_details": job_details[0],
            "perc_dict": perc_dict,
            "pipeline": pipeline,
            "my_database": my_database,
            "job_count": job_count,
        }
        return Response(context)


def Diff(li1, li2):
    return list(set(li1) - set(li2))


class missing_skills(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request

        logger.info("Showing missing skills for the JD " + str(pk))
        user_id = admin_account(request)
        try:
            jd_id = pk
            jd_form = JD_form.objects.filter(id=pk)

        except:
            jd_id = JD_form.objects.filter(user_id_id=user_id).last().id
            jd_form = JD_form.objects.filter(user_id_id=user_id)
        inp1 = str(JD_form.objects.get(id=jd_id).job_role.id)
        logger.info("missing skills for: " + str(inp1))
        try:
            skill_n_exp1 = {}
            for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values(
                "skill", "experience"
            ):
                skill_n_exp1[i["skill"]] = i["experience"]
            skill_n_exp = [skill_n_exp1]
        except:
            skill_n_exp = []
        mand_skill = [
            i["skill"].upper().strip()
            for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values("skill")
        ]
        # mand_skill = [i.strip() for i in mand_skill1]
        mand_skill_exp1 = [
            i["experience"].upper().strip()
            for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values(
                "experience"
            )
        ]

        if len(mand_skill_exp1) == 0:
            mand_skill_expi = []
            for i in range(len(mand_skill)):
                mand_skill_expi.append(0)
        else:
            mand_skill_expi = [i.strip() for i in mand_skill_exp1]

        allskill = mand_skill
        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                a = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                a = json.load(fp)

        unique = [*a[inp1]["database"]]
        missing_db = Diff(unique, allskill)
        missing_db.sort()
        missing_db = str(missing_db)
        missing_db = (
            missing_db.replace("'", "", len(missing_db))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["tool"]]
        missing_tl = Diff(unique, allskill)
        missing_tl.sort()

        missing_tl = str(missing_tl)
        missing_tl = (
            missing_tl.replace("'", "", len(missing_tl))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["programming"]]
        missing_pl = Diff(unique, allskill)
        missing_pl.sort()

        missing_pl = str(missing_pl)
        missing_pl = (
            missing_pl.replace("'", "", len(missing_pl))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["platform"]]
        missing_pf = Diff(unique, allskill)
        missing_pf.sort()

        missing_pf = str(missing_pf)
        missing_pf = (
            missing_pf.replace("'", "", len(missing_pf))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["misc"]]
        missing_ot = Diff(unique, allskill)
        missing_ot.sort()
        missing_ot = str(missing_ot)
        missing_ot = (
            missing_ot.replace("'", "", len(missing_ot))
            .replace("[", "")
            .replace("]", "")
        )

        mand_skill = str(mand_skill)
        tool = list(
            JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=4)
            .values_list("skill", flat=True)
            .distinct()
        )
        database = list(
            JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=1)
            .values_list("skill", flat=True)
            .distinct()
        )
        platform = list(
            JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=2)
            .values_list("skill", flat=True)
            .distinct()
        )
        misc = list(
            JD_skills_experience.objects.filter(category_id=5, jd_id_id=jd_id)
            .values_list("skill", flat=True)
            .distinct()
        )
        programming = list(
            JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=3)
            .values_list("skill", flat=True)
            .distinct()
        )

        mand_skill = (
            mand_skill.replace("'", "", len(mand_skill))
            .replace("[", "")
            .replace("]", "")
        )
        missing_skill_instance = Missing_Skills_Table.objects.create(
            jd_id_id=jd_id,
            missingskill_mand=mand_skill,
            missingskill_pl=missing_pl,
            missingskill_db=missing_db,
            missingskill_tl=missing_tl,
            missingskill_pf=missing_pf,
            missingskill_ot=missing_ot,
        )
        missing_skill_instance.save()
        jd_profile = JD_profile.objects.filter(jd_id_id=jd_id)
        missing_skills_id = (
            Missing_Skills_Table.objects.filter(jd_id=jd_id).last().miss_skill_id
        )
        temp = list(
            Missing_Skills_Table.objects.filter(
                miss_skill_id=missing_skills_id
            ).values()
        )

        context = {
            "object": temp,
            "pk_id": jd_form.values(),
            "jd_profile": jd_profile.values(),
            "object1": mand_skill_expi,
            "skill_n_exp": skill_n_exp,
            "tool_skill": tool,
            "database_skill": database,
            "platform_skill": platform,
            "misc_skill": misc,
            "programming_skill": programming,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        jd = JD_form.objects.filter(id=pk).last()
        skill_exp = request.POST.getlist("skills_exp")[0].split(",")
        skills = request.POST.getlist("skills")[0].split("|")
        # skill_l = [skill_exp[i] for i in range(len(skill_exp)) if i%2 == 0]
        # exp_l = [skill_exp[i] for i in range(len(skill_exp)) if i%2 != 0]
        JD_skills_experience.objects.filter(jd_id_id=jd.id).delete()
        skill_temp = []
        database_skill = request.POST.getlist("database_skill")[0].upper().split(",")
        platform_skill = request.POST.getlist("platform_skill")[0].upper().split(",")
        programming_skill = (
            request.POST.getlist("programming_skill")[0].upper().split(",")
        )
        tool_skill = request.POST.getlist("tool_skill")[0].upper().split(",")
        misc_skill = request.POST.getlist("misc_skill")[0].upper().split(",")

        for s, e in zip(skills, skill_exp):
            # if s.upper() in skills and s.upper() not in skill_temp:
            # skill_temp.append(s.upper())
            if len(s) != 0:
                if s.upper() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=1
                    )
                if s.upper() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=2
                    )
                if s.upper() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=3
                    )
                if s.upper() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=4
                    )
                if s.upper() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=5
                    )

        return Response({"success": True})


class select_ds_or_non_ds(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user, updated_by = admin_account(request)
        feature = client_features_balance.objects.get(
            client_id=user, feature_id_id=10
        ).available_count
        if not company_details.objects.filter(recruiter_id=user).exists():
            return Response({"feature": feature, "url": "company_detail"})
        if not career_page_setting.objects.filter(recruiter_id=user).exists():
            return Response({"feature": feature, "url": "build_career_page"})

        return Response({"feature": feature})


class JD_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request

        if request.GET["ds_role"] == "1":

            result = tmeta_jd_templates.objects.filter(is_ds_role=True).values()
            job_title = tmeta_jd_templates.objects.filter(is_ds_role=True).values_list(
                "job_title", flat=True
            )
        else:

            result = tmeta_jd_templates.objects.filter(is_ds_role=False).values()
            job_title = tmeta_jd_templates.objects.filter(is_ds_role=False).values_list(
                "job_title", flat=True
            )

        return Response({"jd_templates": result, "job_title": job_title})


class candi_invite_status(generics.GenericAPIView):
    def get(self, request, pk):
        request = self.request
        if "interested" in request.GET and "can_id" in request.GET:
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=request.GET["can_id"]
            ).last()
            if request.GET["interested"] == "true":
                invite.is_interested = 1
            elif request.GET["interested"] == "false":
                invite.is_interested = 0
            invite.responded_date = timezone.now()
            invite.save()
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=request.GET["can_id"]
            ).values()[0]
            return Response({"invite": invite})


class career_job_view_api(generics.GenericAPIView):

    def get(self, request, pk):
        request = self.request

        if request.GET["user_id"] != "0":
            login_user = True
        else:
            login_user = False
        if "apply" in request.GET:
            request.session["apply_user"] = 1
        client_id = JD_form.objects.get(id=pk).user_id
        company_detail = company_details.objects.filter(recruiter_id=client_id).values(
            "company_name",
            "company_website",
            "email",
            "address",
            "country__name",
            "state__name",
            "city__name",
            "zipcode",
            "logo",
            "recruiter_id_id",
        )
        try:

            setting = career_page_setting.objects.filter(
                recruiter_id=client_id
            ).values()
        except:
            setting = None
        if not JD_form.objects.filter(id=pk, jd_status_id=1).exists():
            return Response(
                {
                    "success": False,
                    "msg": "jd_inactive",
                    "company_detail": company_detail[0],
                    "setting": setting[0],
                }
            )
        jd_form = JD_form.objects.filter(id=pk, jd_status_id=1)

        jd_form = jd_form.annotate(
            country=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "country__name"
                )
            ),
            state=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "state__name"
                )
            ),
            city=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "city__name"
                )
            ),
        )
        jd_form = jd_form.annotate(
            job_location=Concat(
                "city", V(", "), "state", V(", "), "country", output_field=CharField()
            )
        ).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "job_location",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
        )
        questionnaire = applicant_questionnaire.objects.filter(jd_id_id=pk).values()
        education = JD_qualification.objects.filter(jd_id_id=pk).values()
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        if login_user == True:

            applicant_details = Personal_Info.objects.get(
                user_id_id=request.GET["user_id"]
            )
            applicant_detail = Personal_Info.objects.filter(
                user_id_id=request.GET["user_id"]
            )
            applicant_detail = applicant_detail.annotate(
                image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("user_id"))[:1].values(
                        "image"
                    )
                ),
            ).values(
                "user_id",
                "firstname",
                "lastname",
                "email",
                "contact_no",
                "image",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "Date_of_birth",
                "linkedin_url",
                "career_summary",
                "gender__label_name",
                "updated_at",
                "code_repo",
                "visa_sponsorship",
                "remote_work",
                "type_of_job__label_name",
                "available_to_start__label_name",
                "industry_type__label_name",
                "desired_shift__label_name",
                "curr_gross",
                "current_currency",
                "exp_gross",
                "salary_negotiable",
                "current_country__name",
                "current_state__name",
                "current_city__name",
                "relocate",
            )[
                0
            ]
            additional_detail = Additional_Details.objects.filter(
                application_id=applicant_details
            ).values()[0]
        else:
            applicant_details = None
            applicant_detail = None
            # additional_details=None
            additional_detail = None

        try:
            emp_id = employer_pool.objects.get(
                candidate_id=applicant_details, client_id=client_id
            ).pk
        except:
            emp_id = 0

        try:
            apply_user = request.session["apply_user"]
        except:
            apply_user = 0

        applied_status = 0
        if applicants_status.objects.filter(
            jd_id_id=pk, candidate_id_id=emp_id, status_id__in=[1, 2, 3, 4, 7]
        ).exists():
            applied_status = 1
        current_site = settings.CLIENT_URL

        context = {
            "success": True,
            "jd_form": jd_form[0],
            "education": education,
            "skills": skills,
            "login_user": login_user,
            "applicant_detail": applicant_detail,
            "questionnaire": questionnaire,
            "additional_detail": additional_detail,
            "company_detail": company_detail[0],
            "setting": setting[0],
            "emp_id": emp_id,
            "current_site": str(current_site),
            "applied_status": applied_status,
            "apply_user": apply_user,
        }
        response = Response(context)

        return response

    def post(self, request, pk):
        request = self.request

        applicant_details = Personal_Info.objects.get(user_id=request.user)

        ques_list = request.POST["questionnaire"].split(",")
        try:
            for i in ques_list:
                id_ = i.split(":")[0]
                value = i.split(":")[1]
                applicant_answers.objects.create(
                    qus_id_id=id_, candidate_id=applicant_details, answer=value
                )
        except:
            pass
        cover_letter = applicant_cover_letter_form(request.POST)
        jobs_eeo = jobs_eeo_form(request.POST)
        if cover_letter.is_valid():
            cover_letter = cover_letter.save(commit=False)
            cover_letter.candidate_id = applicant_details
            cover_letter.jd_id_id = pk
            cover_letter.save()
        if jobs_eeo.is_valid():
            jobs_eeo = jobs_eeo.save(commit=False)
            jobs_eeo.jd_id_id = pk
            jobs_eeo.candidate_id = applicant_details
            jobs_eeo.save()

        jd_form = JD_form.objects.get(id=pk)
        client_id = JD_form.objects.get(id=pk).user_id
        skills = Skills.objects.get(application_id=applicant_details)
        try:
            skilld = skills.tech_skill + "," + skills.soft_skill
        except:
            skilld = skills.tech_skill
        location = str(
            applicant_details.city.name
            + ", "
            + applicant_details.state.name
            + ", "
            + applicant_details.country.name
        )

        if employer_pool.objects.filter(
            client_id=client_id,
            email=applicant_details.email,
            can_source_id__in=[1, 2, 3],
        ).exists():
            employer_pool.objects.filter(
                client_id=client_id, email=applicant_details.email
            ).update(
                candidate_id=applicant_details,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=str(
                    Additional_Details.objects.get(
                        application_id=applicant_details
                    ).total_exp_year
                ),
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
        elif employer_pool.objects.filter(
            client_id=client_id, can_source_id=4, candidate_id=applicant_details
        ).exists():
            employer_pool.objects.filter(
                client_id=client_id, email=applicant_details.email
            ).update(
                candidate_id=applicant_details,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                can_source_id=3,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=str(
                    Additional_Details.objects.get(
                        application_id=applicant_details
                    ).total_exp_year
                ),
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
        else:
            employer_pool.objects.create(
                client_id=client_id,
                email=applicant_details.email,
                candidate_id=applicant_details,
                can_source_id=3,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=str(
                    Additional_Details.objects.get(
                        application_id=applicant_details
                    ).total_exp_year
                ),
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
            avail = client_features_balance.objects.get(
                client_id=client_id, feature_id_id=12
            )
            if not avail.available_count == None:
                avail.available_count = avail.available_count - 1
                avail.save()

        try:
            source = request.POST["source_count"]
        except:
            source = "Career Page"

        emp_id = employer_pool.objects.get(
            candidate_id=applicant_details, client_id=client_id
        )
        result = applicant_genarate_json(request, pk=emp_id.id)
        applicants_status.objects.create(
            jd_id_id=pk,
            source=source,
            candidate_id=emp_id,
            status_id_id=1,
            client_id=client_id,
            created_on=timezone.now(),
        )

        applicants_screening_status.objects.create(
            jd_id_id=pk, candidate_id=emp_id, status_id_id=1, client_id=client_id
        )
        request.session["apply_user"] = 2
        data = (
            applicant_details.firstname.title()
            + " has applied for "
            + jd_form.job_title.title()
            + " - "
            + str(jd_form.job_id)
        )
        
        messages.success(request, "test")
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=client_id
            ).career_page_url
        except:
            career_page_url = ""
        response = Response({"success": True})
        return response


class email_preference_api(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        email_preferences = email_preference.objects.filter(
            user_id=request.user
        ).values(
            "user_id",
            "stage_id",
            "is_active",
            "created_at",
            "updated_by",
        )

        meta_email = tmeta_email_preference.objects.all().values()
        context = {
            "success": True,
            "email_preferences": email_preferences,
            "meta_email": meta_email,
        }
        response = Response(context)
        return response

    def post(self, request):
        request = self.request
        email_preference.objects.filter(
            user_id=request.user, stage_id_id=request.POST["stage_id"]
        ).update(is_active=request.POST["is_active"])
        context = {
            "success": True,
            # 'email_preferences':email_preferences,
        }
        response = Response(context)
        return response
