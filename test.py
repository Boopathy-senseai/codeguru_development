from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
from django.views.generic.edit import DeleteView
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate, logout
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.files import File
from django.core.files.base import ContentFile
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.db.models import *

# from PIL import Image
from django.shortcuts import render, get_object_or_404, render_to_response
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from application.forms import *
from jobs.parsing import convert_to_html
from main.forms import *
from login.forms import *
from application.models import *
from main.models import *
from login.models import *

# from dset.models import *
# from usecase.models import *
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
import subprocess
import json
import os, time
import re
import operator
import datetime as dt
from jobs.views import mail_notification
import json
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from django.db import IntegrityError, transaction
from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView,
)
import requests
import ast
from zita import settings
from login.decorators import *

global base_dir
base_dir = settings.BASE_DIR
import logging
from random import choice
from string import ascii_lowercase, digits

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

from django.views.decorators.cache import never_cache

# from application.skill_match import *
# from application.profiling import *
from django.contrib import messages


from collections.abc import Iterable
from application.models import *
from jobs.models import *
from job_pool.models import *


def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten(item):
                yield x.lower().strip()
        else:
            yield item.lower().strip()


def intersection(lst1, lst2):

    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3


def update_skill_match(request):
    time.sleep(1)
    username = request.user
    user_id = User.objects.get(username=username).id
    application_id = Personal_Info.objects.get(user_id=user_id).application_id

    if request.method == "POST":

        try:
            application_skills = (
                Skills.objects.filter(application_id_id=application_id)
                .values("tech_skill")[0]["tech_skill"]
                .split(",")
            )
        except IndexError:
            application_skills = [""]

        project_skills = [
            i[0].split(",")
            for i in Projects.objects.filter(application_id_id=application_id)
            .values_list("work_proj_skills")
            .distinct()
        ]
        work_exp_skills = [
            i[0].split(",")
            for i in Experiences.objects.filter(application_id_id=application_id)
            .values_list("work_tools")
            .distinct()
        ]
        candidate_skill_list = list(
            map(
                lambda x: x.lower(),
                list(
                    set(flatten(application_skills + project_skills + work_exp_skills))
                ),
            )
        )

        matched_jds = Matched_candidates.objects.filter(
            application_id_id=application_id
        ).values_list("jd_list_id", flat=True)
        count = 0
        for jd_list_id in matched_jds:
            try:
                jd_skill_list = list(
                    map(
                        lambda x: x.lower(),
                        JD_list.objects.filter(jd=jd_list_id)
                        .values("mapped_skills")[0]["mapped_skills"]
                        .split(","),
                    )
                )
            except AttributeError:
                jd_skill_list = [""]

            new_match = intersection(candidate_skill_list, jd_skill_list)

            Matched_candidates.objects.filter(
                application_id_id=application_id, jd_list_id_id=jd_list_id
            ).update(skill_match=",".join(map(str, new_match)))
            count += 1

        return HttpResponse("updated skill match")


# Backend Quewry for the preview,profile, and download pages


def get_app_prof_details(u_id, for_exp=False):
    resume_details = {}
    user = User.objects.get(pk=u_id)
    P_info = Personal_Info.objects.get(user_id_id=u_id)
    from login.models import Profile as user_profile_image

    resume_details["profile_url"] = str(
        user_profile_image.objects.get(user_id=u_id).image
    )
    if P_info.lastname == None:
        lastname = ""
    else:
        lastname = P_info.lastname
    try:
        resume_details["full_name"] = P_info.firstname + " " + lastname
        resume_details["email"] = P_info.email
    except:
        resume_details["full_name"] = "Not Given"
        resume_details["email"] = "Not Given"
    if P_info.contact_no == None:
        resume_details["phone_no"] = "Not Given"
    else:
        resume_details["phone_no"] = P_info.contact_no
    if P_info.linkedin_url != None:

        resume_details["linkedin_url"] = P_info.linkedin_url
    if P_info.code_repo != None:
        resume_details["repo"] = P_info.code_repo
    if P_info.career_summary != None:
        resume_details["summary"] = P_info.career_summary

    # projects other
    try:
        projects = []
        pro = Projects.objects.filter(
            work_proj_org_id_id=None,
            application_id_id=P_info.application_id,
            work_proj_type=False,
        )
        for i in pro:
            temp = {}
            temp["org"] = ""
            temp["project_name"] = i.work_proj_name
            temp["client"] = i.work_proj_client
            if i.work_proj_describe != None:

                temp["desc"] = i.work_proj_describe
            else:
                temp["desc"] = ""
            roless = i.work_proj_role
            roless = roless.replace("1).", "").replace("Description :", "")
            for z in range(2, 50):
                roless = roless.replace(str(z) + ").", " \n")
            temp["responsibilities"] = roless.split("\n")
            temp["role"] = i.work_proj_desig
            temp["dur"] = i.work_proj_duration

            if i.work_proj_domain != None:

                temp["domain"] = i.work_proj_domain
            else:
                temp["domain"] = ""
            temp["loc"] = i.work_proj_location
            skills = i.work_proj_skills
            skills = skills.replace("1).", "").replace("<br>", "")
            for z in range(2, 50):
                skills = skills.replace(str(z) + ").", " \n")
            temp["skills"] = skills.split("\n")

            projects.append(temp)
        resume_details["projects"] = projects
    except:
        a = 0

    exp = []
    exp_info = Experiences.objects.filter(
        application_id_id=P_info.application_id
    ).order_by("-is_present", "-from_exp")
    for n, i in enumerate(exp_info):
        temp = {}
        temp["exp_id"] = i.exp_id
        temp["org"] = i.organisations
        if len(i.designation.split(" ")) > 3:
            temp["des"] = " ".join(i.designation.split(" ")[:3])
        else:
            temp["des"] = " ".join(i.designation.split(" "))
        if i.work_location != None:

            temp["loc"] = i.work_location
        else:
            temp["loc"] = ""
        if i.from_exp == None:
            temp["from_exp"] = ""
        else:
            temp["from_exp"] = i.from_exp.strftime("%d %b %Y")
        if i.org_domain != None:

            temp["domain"] = i.org_domain
        else:
            temp["domain"] = ""
        if i.to_exp == None:
            if i.is_present:
                temp["to_exp"] = "Till Date"
            else:
                temp["to_exp"] = ""
        else:
            temp["to_exp"] = i.to_exp.strftime("%d %b %Y")
        roless = i.work_role
        roless = roless.replace("1).", "")
        for a in range(2, 50):
            roless = roless.replace(str(a) + ").", " \n")
        temp["roles"] = roless.split("\n")
        temp["exp_tools"] = i.work_tools
        if i.is_present:
            temp["is_present"] = 1
        else:
            temp["is_present"] = 0
        projects = []
        pro = Projects.objects.filter(work_proj_org_id_id=i.exp_id)
        if len(pro) > 0:
            for z in pro:
                temp1 = {}
                if i.organisations != None:
                    temp1["org"] = i.organisations
                else:
                    temp1["org"] = ""
                temp1["project_name"] = z.work_proj_name
                temp1["client"] = z.work_proj_client
                if z.work_proj_describe != None:

                    temp1["desc"] = z.work_proj_describe
                else:
                    temp1["desc"] = ""
                roless = z.work_proj_role
                roless = roless.replace("1).", "").replace("Description :", "")
                for b in range(2, 50):
                    roless = roless.replace(str(b) + ").", " \n")
                temp1["responsibilities"] = roless.split("\n")
                temp1["role"] = z.work_proj_desig
                temp1["dur"] = z.work_proj_duration
                if z.work_proj_domain != None:

                    temp1["domain"] = z.work_proj_domain
                else:
                    temp1["domain"] = ""
                temp1["loc"] = z.work_proj_location
                skills = z.work_proj_skills
                skills = skills.replace("1).", "").replace("<br>", "")
                for z in range(2, 50):
                    skills = skills.replace(str(z) + ").", " \n")
                temp1["skills"] = skills.split("\n")
                projects.append(temp1)
            temp["projects"] = projects
        exp.append(temp)
    resume_details["exp"] = exp

    edu = []
    try:
        edu_info = Education.objects.filter(application_id_id=P_info.application_id)
        for n, i in enumerate(edu_info):
            temp = {}
            temp["edu_id"] = i.edu_id
            temp["title_spec"] = i.qual_spec
            temp["inst_name"] = i.institute_name
            temp["inst_loc"] = i.institute_location
            temp["qual_title"] = i.qual_title
            temp["percentage"] = i.percentage
            temp["year"] = i.year_completed
            edu.append(temp)
        resume_details["edu"] = edu
    except:
        a = 0

    # skills&tools
    try:
        temp = []
        temp_soft = []
        skill_l = Skills.objects.filter(application_id_id=P_info.application_id)
        skill_id = skill_l.values("id")[0]
        for i in skill_l:
            if i.tech_skill != None and len(i.tech_skill) > 0:
                temp.extend(i.tech_skill.split(","))

            if i.soft_skill != None:
                if len(i.soft_skill) > 0 and i.soft_skill != " ":
                    temp_soft.extend(i.soft_skill.split(","))
                else:
                    temp_soft = 0
            else:
                temp_soft = 0
        temp = sorted(temp)
        resume_details["skills"] = temp
        resume_details["skill_id"] = skill_id
        resume_details["soft_skills"] = temp_soft
    except:
        a = 0

    # certifications&courses
    certi = []
    try:
        courses_info = Certification_Course.objects.filter(
            application_id_id=P_info.application_id
        )
        for i in courses_info:
            temp = {}
            temp["cert_id"] = i.id
            temp["certification_name"] = i.certificate_name
            temp["certificate_by"] = i.certificate_by

            temp["certificate_year"] = str(i.certificate_year)
            certi.append(temp)
        resume_details["certi"] = certi
    except:
        a = 0

    # academic projects
    ac_projects = []

    try:
        ac_proj = Projects.objects.filter(application_id_id=P_info.application_id)

        for i in ac_proj:
            if i.work_proj_type == True:
                temp = {}
                if i.work_proj_org_id_id == None:
                    if i.work_proj_type == False or i.work_proj_type == None:
                        temp["org"] = "Private Project"
                    else:
                        temp["org"] = "Academic Project"
                else:
                    exp = Experiences.objects.get(
                        exp_id=i.work_proj_org_id_id
                    ).organisations

                    temp["org"] = exp

                temp["pro_id"] = i.project_id
                temp["project_name"] = i.work_proj_name
                temp["client"] = i.work_proj_client
                if i.work_proj_describe != None:
                    temp["desc"] = i.work_proj_describe
                else:
                    temp["desc"] = " "
                roless = i.work_proj_role
                roless = roless.replace("1).", "").replace("Description :", "")
                for z in range(2, 50):
                    roless = roless.replace(str(z) + ").", " \n")
                temp["responsibilities"] = roless.split("\n")
                temp["role"] = i.work_proj_desig
                temp["dur"] = i.work_proj_duration
                if i.work_proj_domain != None:

                    temp["domain"] = i.work_proj_domain
                else:
                    temp["domain"] = ""
                temp["loc"] = i.work_proj_location
                skills = i.work_proj_skills
                skills = skills.replace("1).", "").replace("<br>", "")
                for z in range(2, 50):
                    skills = skills.replace(str(z) + ").", " \n")
                temp["skills"] = skills.split("\n")
                ac_projects.append(temp)
            resume_details["ac_projects"] = ac_projects

    except:
        a = 0

    proj_list = []
    try:
        ac_proj = Projects.objects.filter(application_id_id=P_info.application_id)

        for i in ac_proj:
            temp = {}
            if i.work_proj_org_id_id == None:
                if i.work_proj_type == False or i.work_proj_type == None:
                    temp["org"] = "Private Project"
                else:
                    temp["org"] = "Academic Project"
            else:
                exp = Experiences.objects.get(
                    exp_id=i.work_proj_org_id_id
                ).organisations

                temp["org"] = exp
            temp["pro_id"] = i.project_id
            temp["project_name"] = i.work_proj_name
            temp["client"] = i.work_proj_client
            if i.work_proj_describe != None:
                temp["desc"] = i.work_proj_describe
            else:
                temp["desc"] = " "
            roless = i.work_proj_role
            roless = roless.replace("1).", "").replace("Description :", "")
            for z in range(2, 50):
                roless = roless.replace(str(z) + ").", " \n")
            temp["responsibilities"] = roless.split("\n")
            temp["role"] = i.work_proj_desig
            temp["dur"] = i.work_proj_duration
            if i.work_proj_domain != None:

                temp["domain"] = i.work_proj_domain
            else:
                temp["domain"] = ""
            temp["loc"] = i.work_proj_location
            skills = i.work_proj_skills
            skills = skills.replace("1).", "").replace("<br>", "")
            for z in range(2, 50):
                skills = skills.replace(str(z) + ").", " \n")
            temp["skills"] = skills.split("\n")
            proj_list.append(temp)
        resume_details["proj_list"] = proj_list
    except:
        a = 0

    # Contributions
    contribs = []
    try:
        contrib = Contributions.objects.filter(application_id_id=P_info.application_id)
        for i in contrib:
            temp = {}
            temp["cont_id"] = i.contributions_id
            temp["contrib_text"] = i.contrib_text
            temp["contrib_type"] = i.contrib_type.value
            contribs.append(temp)
        resume_details["contribs"] = contribs
    except:
        a = 0
    # Internships
    internships = []
    try:
        internship = Fresher.objects.filter(application_id_id=P_info.application_id)
        for i in internship:
            temp = {}
            temp["fre_id"] = i.id
            temp["org"] = i.intern_org
            temp["project_name"] = i.intern_project
            temp["client"] = i.intern_client
            roless = i.intern_proj_describe.split("\n")
            temp["desc"] = roless
            temp["role"] = i.intern_role
            temp["dur"] = i.intern_duration
            temp["domain"] = i.intern_domain
            temp["loc"] = i.intern_location
            temp["tools"] = i.intern_tools_prg_lng

            internships.append(temp)
        resume_details["internships"] = internships
    except:
        a = 0

    if for_exp:
        prof = list(
            Visualize.objects.filter(application_id_id=P_info.application_id).values(
                "business_intelligence",
                "data_analysis",
                "data_engineering",
                "devops",
                "machine_learning",
                "others",
            )
        )
        return (user, resume_details, prof)
    else:

        return (user, resume_details)


# This function for the preview page
@never_cache
@login_required
@candidate_required
def Pre_Preview(request):
    userid = request.user.id
    user, resume_details = get_app_prof_details(u_id=userid, for_exp=False)
    # request.session['email'] = 1

    try:
        email = request.session["email"]
    except KeyError:
        if Personal_Info.objects.get(user_id=request.user).current_country == None:
            email = 1
        else:
            email = 2
    # email = 1
    current_site = get_current_site(request)
    user_id = User_Info.objects.get(user_id_id=userid)
    if user_id.application_status == 0:
        user_id.application_status = 50
        user_id.save()

    user_info = User_Info.objects.filter(user_id_id=userid)
    till_date = 0
    is_present = Experiences.objects.filter(
        application_id_id__user_id_id=userid, is_present=1
    ).order_by("exp_id")
    if is_present.count() > 1:
        till_date = is_present.values("exp_id")[0]["exp_id"]

    if request.method == "POST" and "preview_button" in request.POST:
        user_id = User_Info.objects.get(user_id_id=userid)
        if user_id.application_status == 100:
            pass
        else:
            user_id.application_status = 90
        user_id.save()
        response = redirect("main:dashboard_main")
        return response
    try:
        jd_id = request.COOKIES["jd-id"]
    except:
        jd_id = None
    # Profiling and matching function
    if request.method == "POST" and "apply_job" in request.POST:
        application_id = Personal_Info.objects.get(user_id=request.user)
        jd_id = request.COOKIES["jd-id"]
        emp_id = request.COOKIES["emp-id"]
        user_info = User_Info.objects.filter(user_id=request.user).update(
            employer_id=int(emp_id)
        )
        jd_title = JD_form.objects.get(id=jd_id).job_title
        request.session["apply_user"] = 1
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id_id=int(emp_id)
            ).career_page_url
        except:
            career_page_url = ""
        response = redirect(
            "jobs:career_job_view",
            pk=int(jd_id),
            job_title=jd_title,
            url=career_page_url,
        )
        response.delete_cookie("jd-id")
        response.delete_cookie("emp-id")
        return response

    personal = Personal_Info.objects.get(user_id=userid)

    try:
        industry_type = tmeta_industry_type.objects.filter(
            id=personal.industry_type.id
        ).values("value")[0]["value"]
    except AttributeError:
        industry_type = "Any"

    try:

        additional_detail = Additional_Details.objects.get(
            application_id=personal.application_id
        )
    except Additional_Details.DoesNotExist:
        additional_detail = ""

    context = {
        "obj": resume_details,
        "user": user,
        "additional_detail": additional_detail,
        "personal": personal,
        "industry_type": industry_type,
        "user_id": user_id,
        "jd_id": jd_id,
        "user_info": json.dumps(list(user_info.values()), cls=DjangoJSONEncoder),
        "email": json.dumps(email, cls=DjangoJSONEncoder),
        "verify": json.dumps(email, cls=DjangoJSONEncoder),
        "till_date": json.dumps(till_date, cls=DjangoJSONEncoder),
    }
    response = render(request, "application/pre_preview.html", context)

    return response


# This function for the Download the profile page (Experiences)


@login_required
@candidate_required
def prof_download_exp(request):

    resume_details = {}
    user_id = request.user.id
    current_site = get_current_site(request)
    username = request.user
    application_id = Personal_Info.objects.get(user_id=user_id).application_id
    user_info = User_Info.objects.get(user_id_id=user_id)
    roles = user_info.recommended_role.split(",")
    main_prof_dict = {}
    main_claimed_prof = {}
    evaluation = {}
    avg_score = {}
    usecase_success = []
    if len(user_info.recommended_role) > 0:
        for r in roles:
            ds_main_roles = tmeta_ds_main_roles.objects.get(tag_name=r).id

            if Test_Assign.objects.filter(
                user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
            ).exists():
                stat = 1  ## test page is already started/ done.
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
                selected_role = r
                claimed_prof = {
                    i["Skill"].lower(): i["level"]
                    for i in Tech_proficiency.objects.filter(
                        application_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).values("Skill", "level")
                }
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
                            order.get(
                                i["question_id_id__difficulty_level__label_name"], 0
                            ),
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
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=1)
                            )
                            * 100,
                            med_percent=Sum(
                                "marks", filter=Q(question_id_id__difficulty_level=2)
                            )
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=2)
                            )
                            * 100,
                            hard_percent=Sum(
                                "marks", filter=Q(question_id_id__difficulty_level=3)
                            )
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=3)
                            )
                            * 100,
                        )
                    )

                    prof_dict = {}
                    for section_dict in prof_res:
                        sec_name = section_dict["section__label_name"]
                        prof_level = "Fresher"
                        if section_dict["easy_percent"]:
                            if section_dict["easy_percent"] > 60:
                                prof_level = "Beginner"
                        if section_dict["med_percent"]:
                            if section_dict["med_percent"] > 60:
                                prof_level = "Intermediate"
                        if section_dict["hard_percent"]:
                            if section_dict["hard_percent"] > 60:
                                prof_level = "Advanced"

                        prof_dict[sec_name.lower()] = prof_level
                    if parameters.is_coding:
                        for i in range(len(section_arr_table)):
                            if section_arr_table[i][0] == "coding":
                                code_prof = section_arr_table[i][4]
                            else:
                                code_prof = 1

                        if code_prof == 0:
                            code_level = "Fresher"
                        elif code_prof == 50:
                            code_level = "Intermediate"
                        elif code_prof == 100:
                            code_level = "Advanced"
                        else:
                            code_level = "Fresher"

                        prof_dict.update({"coding": code_level})
                    created_on = Test_Assign.objects.get(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    ).created_on
                    prof_dict.update({"created_on": created_on})

                else:
                    prof_dict = ""
                    sect_dict_gauge = ""
                    claimed_prof = claimed_prof

            else:
                stat = 0  ## test page hasn't started
                dset_status = 0
                selected_role = ""
                prof_dict = ""
                sect_dict_gauge = ""
                claimed_prof_status = (
                    1
                    if Tech_proficiency.objects.filter(
                        application_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).exists()
                    else 0
                )
                claimed_prof = (
                    {
                        i["Skill"].lower(): i["level"]
                        for i in Tech_proficiency.objects.filter(
                            application_id_id__user_id_id=user_id,
                            role_id_id=ds_main_roles,
                            active_test=1,
                        ).values("Skill", "level")
                    }
                    if claimed_prof_status == 1
                    else ""
                )
            main_prof_dict.update({r: prof_dict})
            main_claimed_prof.update({r: claimed_prof})

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
                    avg_metrics_score.objects.filter(role_name=r).values()
                )
                evaluation.update({r: list(evaluation_list.values())})
                avg_score.update({r: list(avg_score_list)})

            else:
                usecase_status = 0
            usecase_success.append(usecase_status)

    else:
        selected_role = ""

    # if Usecase.objects.filter(application_id = application_id,role_id_id=ds_main_roles,active_test=1).exists():
    #     usecase_list = True
    # else:
    #     usecase_list = None

    personal = Personal_Info.objects.get(user_id=user_id)

    show_jp = 1 if personal.available_to_start.lower() != "unavailable" else 0

    try:
        industry_type = tmeta_industry_type.objects.filter(
            id=personal.industry_type.id
        ).values("value")[0]["value"]
    except AttributeError:
        industry_type = "Any"
    user, resume_details, prof = get_app_prof_details(u_id=user_id, for_exp=True)

    context = {
        "selected_role": json.dumps(selected_role, cls=DjangoJSONEncoder),
        "prof_dict": main_prof_dict,
        "claimed_prof": main_claimed_prof,
        "usecase_success": usecase_success,
        "recommended_role": user_info.recommended_role,
        "show_jp": show_jp,
        "val_2recuriter": json.dumps(
            user_info.val_status_2recruiter, cls=DjangoJSONEncoder
        ),
        "personal": personal,
        "industry_type": industry_type,
        "user": user,
        "obj": resume_details,
        "username": username,
        "domain": current_site.domain,
        "doughnutchart": json.dumps(prof, cls=DjangoJSONEncoder),
        "evaluation_list": json.dumps(evaluation, cls=DjangoJSONEncoder),
        "avg_score": json.dumps(avg_score, cls=DjangoJSONEncoder),
    }
    return render(request, "index-experience.html", context)


# This function for the Download the profile page (Fresher)
@login_required
@candidate_required
def prof_download_fresher(request):
    userid = request.user.id
    resume_details = {}
    userid = request.user.id
    user, resume_details = get_app_prof_details(u_id=userid, for_exp=False)

    return render(request, "index-fresher.html", {"obj": resume_details, "user": user})


# This function for the Candidate Profile page
def Profile_Page(request, username):

    pk = User.objects.get(username=username).id
    application_id = Personal_Info.objects.get(user_id=pk).application_id
    user_info = User_Info.objects.get(user_id_id=pk)
    user_id = pk
    is_authenticated = 0
    if request.user.is_authenticated and request.user.is_staff == False:
        is_authenticated = 1
    if request.method == "POST":
        user_details = User_Info.objects.get(username=username)
        Contact_Form.objects.create(
            viewed_profile=username,
            canditate_user_id=user_details.user_id_id,
            name=request.POST["name"],
            phone=request.POST["phone"],
            email=request.POST["email"],
            subject=request.POST["subject"],
            message=request.POST["message"],
        )

        body = (
            "Viewed canditate profile:  "
            + username
            + "\n"
            + "Canditate user ID: "
            + str(user_details.user_id_id)
            + "\n"
            + "Name: "
            + request.POST["name"]
            + "\n"
            + "Phone: "
            + request.POST["phone"]
            + "\n"
            + "Email: "
            + request.POST["email"]
            + "\n"
            + "Subject: "
            + request.POST["subject"]
            + "\n"
            + "Message: "
            + request.POST["message"]
        )
        send_mail("Canditate Profile Enqiry", body, "info@zita.ai", ["info@zita.ai"])
        return HttpResponse(1)
    # ds_main_roles = tmeta_ds_main_roles.objects.get(tag_name=user_info.selected_role).id
    recom_role = Recommended_Role.objects.filter(user_id=user_id)
    main_prof_dict = {}
    main_claimed_prof = {}
    evaluation = {}
    avg_score = {}
    usecase_success = []
    if recom_role.exists():
        for r in recom_role:
            ds_main_roles = r.recommended_role.id

            if Test_Assign.objects.filter(
                user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
            ).exists():
                stat = 1  ## test page is already started/ done.
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
                claimed_prof = {
                    i["Skill"].lower(): i["level"]
                    for i in Tech_proficiency.objects.filter(
                        application_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).values("Skill", "level")
                }
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
                            order.get(
                                i["question_id_id__difficulty_level__label_name"], 0
                            ),
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
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=1)
                            )
                            * 100,
                            med_percent=Sum(
                                "marks", filter=Q(question_id_id__difficulty_level=2)
                            )
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=2)
                            )
                            * 100,
                            hard_percent=Sum(
                                "marks", filter=Q(question_id_id__difficulty_level=3)
                            )
                            / Count(
                                "marks", filter=Q(question_id_id__difficulty_level=3)
                            )
                            * 100,
                        )
                    )

                    prof_dict = {}
                    for section_dict in prof_res:
                        sec_name = section_dict["section__label_name"]
                        prof_level = "Fresher"
                        if section_dict["easy_percent"]:
                            if section_dict["easy_percent"] > 60:
                                prof_level = "Beginner"
                        if section_dict["med_percent"]:
                            if section_dict["med_percent"] > 60:
                                prof_level = "Intermediate"
                        if section_dict["hard_percent"]:
                            if section_dict["hard_percent"] > 60:
                                prof_level = "Advanced"

                        prof_dict[sec_name.lower()] = prof_level
                    if parameters.is_coding:
                        for i in range(len(section_arr_table)):
                            if section_arr_table[i][0] == "coding":
                                code_prof = section_arr_table[i][4]
                            else:
                                code_prof = 1

                        if code_prof == 0:
                            code_level = "Fresher"
                        elif code_prof == 50:
                            code_level = "Intermediate"
                        elif code_prof == 100:
                            code_level = "Advanced"
                        else:
                            code_level = "Fresher"

                        prof_dict.update({"coding": code_level})

                    created_on = Test_Assign.objects.get(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    ).created_on.strftime(" %d %B %Y")
                    prof_dict.update({"dset_date": created_on})
                    try:
                        usecase = Usecase.objects.get(
                            application_id=application_id,
                            role_id_id=ds_main_roles,
                            active_test=1,
                        )
                    except:
                        usecase = None

                    if Usecase_evaluation.objects.filter(usecase_id=usecase).exists():
                        # if Usecase_evaluation.objects.filter(upload_id=application_id, role_id_id=ds_main_roles,active_test=1).exists():
                        usecase_date = Sloved_Usecase.objects.get(
                            upload_id=application_id,
                            role_id_id=ds_main_roles,
                            active_test=1,
                        ).updated_at.strftime(" %d %B %Y")

                        prof_dict.update({"usecase_date": usecase_date})
                    else:
                        prof_dict.update({"usecase_date": 0})

                else:
                    prof_dict = ""
                    sect_dict_gauge = ""
                    claimed_prof = claimed_prof

            else:
                stat = 0  ## test page hasn't started
                dset_status = 0
                prof_dict = ""
                sect_dict_gauge = ""
                claimed_prof_status = (
                    1
                    if Tech_proficiency.objects.filter(
                        application_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).exists()
                    else 0
                )
                claimed_prof = (
                    {
                        i["Skill"].lower(): i["level"]
                        for i in Tech_proficiency.objects.filter(
                            application_id_id__user_id_id=user_id,
                            role_id_id=ds_main_roles,
                            active_test=1,
                        ).values("Skill", "level")
                    }
                    if claimed_prof_status == 1
                    else ""
                )
            main_prof_dict.update({r.recommended_role.tag_name: prof_dict})
            main_claimed_prof.update({r.recommended_role.tag_name: claimed_prof})
            try:
                usecase = Usecase.objects.get(
                    application_id=application_id,
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
                    {r.recommended_role.tag_name: list(evaluation_list.values())}
                )
                avg_score.update({r.recommended_role.tag_name: list(avg_score_list)})

            else:
                usecase_status = 0
            usecase_success.append(usecase_status)

    application_id = Personal_Info.objects.get(user_id=user_id).application_id
    user, resume_details = get_app_prof_details(u_id=user_id, for_exp=False)
    personal = Personal_Info.objects.get(user_id=user_id)
    if personal.available_to_start == None or personal.available_to_start.id != 5:
        show_jp = 1
    else:
        show_jp = 0
    try:
        industry_type = tmeta_industry_type.objects.filter(
            id=personal.industry_type.id
        ).values("value")[0]["value"]
    except AttributeError:
        industry_type = "Any"
    info = list(User_Info.objects.filter(user_id_id=user_id).values())
    prof = list(
        Visualize.objects.filter(application_id_id=application_id).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
    )
    context = {
        "user_info": user_info,
        "obj": resume_details,
        "user": user,
        "personal": personal,
        "industry_type": industry_type,
        "prof_dict": main_prof_dict,
        "show_jp": show_jp,
        "claimed_prof": main_claimed_prof,
        "is_authenticated": is_authenticated,
        "usecase_success": usecase_success,
        "val_2recuriter": json.dumps(
            user_info.val_status_2recruiter, cls=DjangoJSONEncoder
        ),
        "evaluation_list": json.dumps(evaluation, cls=DjangoJSONEncoder),
        "avg_score": json.dumps(avg_score, cls=DjangoJSONEncoder),
        "prof": json.dumps(prof, cls=DjangoJSONEncoder),
        "info": json.dumps(info, cls=DjangoJSONEncoder),
    }
    return render(request, "main/profile.html", context)


# Resume paser API connection and Parcing


def parsing(filename):
    tmp_path = os.getcwd()
    headers = {"Authorization": settings.rp_api_auth_token}

    url = settings.rp_api_url

    # files = {'resume_file': open('/home/server/zita/django/zita/media/resume/'+filename,'rb')}

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
    # with open('/home/server/zita/django/zita/media/SOT_OUT/'+filename+'.json', 'w') as fp:
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

    os.chdir(tmp_path)

    return sentence_list


# This function for Personal information page


@login_required
@candidate_required
def Personal_Information(request):

    user_info = User.objects.get(user_id=request.user)

    status = User_Info.objects.get(user_id=request.user).application_status
    logger.info(
        "logged-in user of personal-info page and status: "
        + str(user_info.id)
        + "&"
        + str(status)
    )
    if status < 10:

        if request.method == "POST":
            form_upload = Upload_resume(request.POST, request.FILES)
            if form_upload.is_valid():
                logger.info("foem_upload is valid")
                temp = form_upload.save(commit=False)
                temp.user_id = User.objects.get(user_id=request.user)
                temp.upload_id_id = user_info.id
                temp.save()
                filepath = form_upload.instance.resume_file.path

                file_name = os.path.splitext(os.path.basename(filepath))
                global filename
                filename = "".join(list(file_name))
                s_time = datetime.now()
                sentences_list = parsing(filename)
                # logger.info('Time taken to parse',(datetime.now()-s_time).total_seconds())
                sentences_list = ast.literal_eval(sentences_list)

                for a in sentences_list:
                    resume_data_upload = IL_RP_Output()
                    resume_data_upload.user_id_id = User.objects.get(
                        username=request.user
                    ).id
                    resume_data_upload.predicted_sentence = a[0]
                    resume_data_upload.model_name = a[1]
                    resume_data_upload.entity_text = a[2]
                    resume_data_upload.entity_label = a[3]
                    resume_data_upload.save()
                # logger.info('Time taken to convert',(datetime.now()-s_time).total_seconds())

                return redirect("application:pre_resume")
        else:
            form_upload = Upload_resume()

        if request.method == "GET":

            form = Personal_Info_Form()
            form2 = Additional_Details_Form()
            logger.info("intialized personal_info and additional_details forms")
        else:
            logger.info("In post request of form submission")
            post_data = request.POST.copy()

            form = Personal_Info_Form(request.POST)
            form2 = Additional_Details_Form(request.POST)

            try:
                if form.is_valid() and form2.is_valid():
                    request.session["form_data"] = post_data
                    logger.info(
                        "stored form data to session as forms are valid, redirecting to job_preference page"
                    )
                    return redirect("application:job_preference")
            except Exception as e:
                logger.error("failed form validation  " + str(e))

        form.fields["firstname"].initial = User.objects.get(
            username=request.user
        ).first_name
        form.fields["lastname"].initial = User.objects.get(
            username=request.user
        ).last_name
        form.fields["email"].initial = User.objects.get(username=request.user).email

    else:
        return redirect("application:pre_preview")

    return render(
        request,
        "application/personal_info.html",
        {"form2": form2, "form": form, "form_upload": form_upload},
    )


## function to merge two dictionalries
##arguments: dictionary1 and dictionary2 || return: new merged dictionary
def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


## function of my job preference page/form
## arguments: HTTP request || return: form submission
def job_preference(request):
    logger.info("in job_preference")

    user_id = User.objects.get(username=request.user).id
    logger.info("logged-in used of my job preference page: " + str(user_id))

    try:
        form_data = request.session["form_data"]

    except UnboundLocalError as ule:
        logger.error("Error: Local variable referred before assignment" + str(ule))
        return HttpResponse(
            "Seems you have not saved Personal Info data properly, Please go back and try to save it again"
        )

    except Exception as e:
        logger.error("couldn't initiate form variables due to " + str(e))
        return HttpResponse(
            "Seems you have not saved Personal Info data properly, Please go back and try to save it again"
        )

    if request.method == "GET":

        jp_form = My_Job_Preference_Form()
        logger.info("initialized my job preference form")

    else:

        jp_form = My_Job_Preference_Form(request.POST)
        pi_form = Personal_Info_Form(form_data)
        ad_form = Additional_Details_Form(form_data)

        if pi_form.is_valid() and ad_form.is_valid() and jp_form.is_valid():
            logger.info("Three forms are valid")

            try:
                with transaction.atomic():
                    temp = pi_form.save(commit=False)
                    temp.user_id = User.objects.get(username=request.user)
                    username = request.user
                    user_id = User_Info.objects.get(username=username)
                    user_id.application_status = 50
                    user_id.applicant_status_id = 2
                    user = User.objects.get(username=request.user)
                    user.first_name = temp.firstname
                    user.last_name = temp.lastname
                    user.save()
                    user_id.save()

                    temp2 = jp_form.save(commit=False)
                    temp.curr_gross = (
                        None
                        if type(temp2.curr_gross) == str and len(temp2.curr_gross) == 0
                        else temp2.curr_gross
                    )
                    temp.exp_gross = temp2.exp_gross
                    temp.save()

                    application_obj = Personal_Info.objects.get(
                        user_id=user_id.user_id_id
                    )

                    jp_form = My_Job_Preference_Form(
                        request.POST, instance=application_obj
                    )
                    temp2 = jp_form.save(commit=False)
                    temp2.curr_gross = (
                        None
                        if type(temp2.curr_gross) == str and len(temp2.curr_gross) == 0
                        else temp2.curr_gross
                    )
                    temp2.save()

                    temp3 = ad_form.save(commit=False)
                    user_id2 = User.objects.get(username=username).id
                    temp3.application_id = Personal_Info.objects.get(user_id=user_id2)

                    temp3.save()
                    try:
                        from_db = request.session["from_db"]
                    except KeyError:
                        from_db = 0
                    if from_db == 1:
                        return redirect("application:pre_population")
                    else:
                        return redirect("/application/edit/#about")

            except IntegrityError as e:
                logger.error(
                    "Transaction of storing form data into DB got failed due to error : ",
                    e,
                )
                transaction.rollback()
        else:
            logger.error(
                "forms have errors in order pi_form,ad_form,jp_form ",
                pi_form.errors,
                ad_form.errors,
                jp_form.errors,
            )

    return render(request, "application/job_preference.html", {"jp_form": jp_form})


@login_required
@candidate_required
def update_job_preference(request):
    user_id = request.user

    try:
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        application_status = User_Info.objects.get(user_id=user_id).application_status
    except ObjectDoesNotExist:
        pass

    if request.method == "POST":
        temp = Personal_Info.objects.filter(user_id=user_id).first()

        jp_form = My_Job_Preference_Form(request.POST, instance=temp)
        hidden_val = request.POST["jp_hidden"]
        if jp_form.is_valid():
            username = request.user
            temp = jp_form.save(commit=False)
            temp.user_id = request.user
            temp.curr_gross = (
                None
                if type(temp.curr_gross) == str and len(temp.curr_gross) == 0
                else temp.curr_gross
            )
            temp.save()
            emp_id = User_Info.objects.get(user_id=user_id).employer_id
            location = str(
                temp.current_city.name
                + ", "
                + temp.current_state.name
                + ", "
                + temp.current_country.name
            )

            employer_pool.objects.filter(
                client_id_id=emp_id, candidate_id=temp.application_id
            ).update(
                relocate=temp.relocate,
                location=location,
                exp_salary=temp.exp_gross,
                job_type=temp.type_of_job,
            )
            if int(hidden_val) == 1:
                return redirect("main:dashboard_main")
            else:
                return redirect("application:pre_preview")

    else:

        temp = Personal_Info.objects.filter(user_id=user_id).first()
        jp_form = My_Job_Preference_Form(instance=temp)

    # jp_form
    return render(
        request, "application/update_job_preference.html", {"jp_form": jp_form}
    )


# This function for candidate pre profiling page
@login_required
@candidate_required
def pre_resumeView(request):

    try:

        user_id = request.user
        f_name = request.user.first_name
        f_save = False

        if request.method == "GET":

            user_id = request.user

            form_upload = Myfiles.objects.filter(upload_id=user_id).order_by("-id")[0]
            filepath_str = form_upload.resume_file

            file_path = str(filepath_str)

            filepath = file_path.split("/")
            filename = filepath[1]
            try:
                json_data = open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json")
                resume_data = open(
                    base_dir + "/" + "media/SOT_OUT/" + filename + "_data.json"
                )
                # json.dump(sample, fp)
            except:
                json_data = open(
                    os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json"
                )
                resume_data = open(
                    base_dir + "/" + "media/SOT_OUT/" + filename + "_data.json"
                )

            data = json.load(json_data)
            resume_text = json.load(resume_data)
            form_upload.resume_text = str(resume_text)
            form_upload.save()
            try:
                lab = [*data["Experience"].keys()]
                work_role = []
                for k in lab:
                    for l in [*data["Experience"][k]]:
                        if l.strip().startswith("Rol"):
                            work_role.append(data["Experience"][k][l])
            except:
                work_role = [""]
            try:
                lab = [*data["Project"].keys()]
                pro_role = []
                for k in lab:
                    # pro_role= []
                    for l in [*data["Project"][k]]:
                        if l.strip().startswith("Rol"):
                            pro_role.append(data["Project"][k][l])

            except:
                pro_role = [""]
            try:
                output = work_role + pro_role
                output_pro = []
                for o in output:
                    for o_split in o.split("#*#"):
                        output_pro.append(o_split)
                # output = [o_split for o_split in o.split() for o in output]
                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = output_pro
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                profiles = result.json()["profiles"]
                profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                profiles["data_analysis"] = profiles.pop("Data_Analysis")
                profiles["data_eng"] = profiles.pop("Data_Engineering")
                profiles["devops"] = profiles.pop("Dev_Ops")
                profiles["ml_model"] = profiles.pop("Machine_Learning")
            except:
                profiles = [""]

            form = Personal_Info_Form()
            form2 = Additional_Details_Form()

            form.fields["firstname"].initial = User.objects.get(
                username=request.user
            ).first_name
            form.fields["lastname"].initial = User.objects.get(
                username=request.user
            ).last_name
            form.fields["email"].initial = User.objects.get(username=request.user).email

            try:
                form.fields["Date_of_birth"].initial = data["Personal"][
                    "Date of Birth"
                ].split("-")[0]
            except KeyError:
                pass
            try:
                form.fields["linkedin_url"].initial = data["Personal"]["LinkedIn"]
            except KeyError:
                pass
            try:
                form.fields["code_repo"].initial = data["Personal"]["Code Repo"]
            except KeyError:
                pass

        else:
            post_data = request.POST.copy()

            form = Personal_Info_Form(request.POST, request.FILES)
            form2 = Additional_Details_Form(request.POST)
            # form3 = My_Job_Preference_Form(request.POST)
            profiles = [""]
            form_upload = Myfiles.objects.filter(upload_id=user_id).order_by("-id")[0]
            filepath_str = form_upload.resume_file
            file_path = str(filepath_str)
            filepath = file_path.split("/")
            filename = filepath[1]

            try:
                json_data = open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json")
            except:
                json_data = open(
                    os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json"
                )
            data = json.load(json_data)
            try:
                lab = [*data["Experience"].keys()]
                work_role = []
                for k in lab:

                    for l in [*data["Experience"][k]]:
                        if l.strip().startswith("Rol"):
                            work_role.append(data["Experience"][k][l])
            except:
                work_role = [""]
            try:
                lab = [*data["Project"].keys()]
                pro_role = []
                for k in lab:
                    # pro_role= []
                    for l in [*data["Project"][k]]:
                        if l.strip().startswith("Rol"):
                            pro_role.append(data["Project"][k][l])

            except:
                pro_role = [""]

            try:
                output = work_role + pro_role
                # output= work_role+pro_role
                output_pro = []
                for o in output:
                    for o_split in o.split("#*#"):
                        output_pro.append(o_split)
                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = output_pro
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                profiles = result.json()["profiles"]
                profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                profiles["data_analysis"] = profiles.pop("Data_Analysis")
                profiles["data_eng"] = profiles.pop("Data_Engineering")
                profiles["devops"] = profiles.pop("Dev_Ops")
                profiles["ml_model"] = profiles.pop("Machine_Learning")
            except:
                profiles = [""]
            logger.info("validating forms - RP")
            if form.is_valid() and form2.is_valid():
                logger.info("personal_info is valid on RP parsing")
                request.session["form_data"] = post_data
                request.session["from_db"] = 1

                # temp = form.save(commit = False)

                # temp.user_id = User.objects.get(username = request.user)

                # temp.save()
                # f_save = True
                # username = request.user
                # user_id = User_Info.objects.get(username = username)
                # user_id.application_status = 10
                # user_id.save()
                # temp.save()
                # temp2 = form2.save(commit = False)
                # user_id2 = User.objects.get(username = username).id
                # temp2.application_id = Personal_Info.objects.get(user_id = user_id2)
                # temp2.save()

                return redirect("application:job_preference")
    except:
        messages.warning(request, "Upload a valid file format")
        return redirect("application:personal_info")

    data_ui = {
        "profiles": json.dumps(profiles, cls=DjangoJSONEncoder),
        "form": form,
        "form2": form2,
    }

    return render(request, "application/personal_info.html", data_ui)


# This function for store the Pre population details into Database


def pre_population(request):

    # try:

    user_id = request.user
    # try:
    application_id = Personal_Info.objects.get(user_id=user_id).application_id
    # except:
    # messages.warning(request, 'Note that you have already submitted your profile. Please contact support team')
    # return redirect('application:personal_info')
    form_upload = Myfiles.objects.filter(upload_id=user_id).order_by("-id")[0]
    filepath_str = form_upload.resume_file
    file_path = str(filepath_str)
    filepath = file_path.split("/")
    filename = filepath[1]
    try:
        json_data = open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json")
    except:
        json_data = open(os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json")
    data2 = json.load(json_data)
    Projects.objects.filter(application_id_id=application_id).delete()
    Education.objects.filter(application_id_id=application_id).delete()
    Experiences.objects.filter(application_id_id=application_id).delete()
    Skills.objects.filter(application_id_id=application_id).delete()
    try:
        ##_______________________________Education_______________________________________________________#

        lab = [*data2["Qualification"].keys()]
        for k in lab:
            qualification = []
            specialization = []
            institute = []
            year_completed = []
            percentage = []
            location = []

            for l in [*data2["Qualification"][k]]:

                if l.strip().startswith("Qu"):
                    qual = ""
                    if data2["Qualification"][k][l].lower().strip() in settings.ug:
                        qual = "Bachelors"
                    if data2["Qualification"][k][l].lower().strip() in settings.pg:
                        qual = "Masters"
                    if data2["Qualification"][k][l].lower().strip() in settings.phd:
                        qual = "Doctorate"
                    qualification.append(qual)

                if l.strip().startswith("Spe"):
                    specialization.append(data2["Qualification"][k][l])

                if l.strip().startswith("Ins"):
                    institute.append(data2["Qualification"][k][l])

                if l.strip().startswith("Ye"):
                    year_completed.append(data2["Qualification"][k][l])

                if l.strip().startswith("Per"):
                    percentage.append(data2["Qualification"][k][l])

                if l.strip().startswith("Lo"):
                    location.append(data2["Qualification"][k][l])

            if len(qualification) > 0:
                qualification = qualification
            else:
                qualification = [""]
            if len(specialization) > 0:
                specialization = specialization
            else:
                specialization = [""]

            if len(institute) > 0:
                institute = institute
            else:
                institute = [""]
            if len(year_completed) > 0:
                year_completed = year_completed
            else:
                year_completed = [""]
            if len(percentage) > 0:
                percentage = percentage
            else:
                percentage = [""]
            if len(location) > 0:
                location = location
            else:
                location = [""]

            Education.objects.create(
                application_id_id=application_id,
                qual_title=qualification[0],
                qual_spec=specialization[0],
                institute_name=institute[0],
                institute_location=location[0],
                year_completed=year_completed[0],
                percentage=percentage[0],
            )

    except:
        pass

    # __________________________________________Experience________________________________________________

    try:
        lab = [*data2["Experience"].keys()]

        for k in lab:

            organisation = []
            designation = []
            work_location = []
            work_role = []
            from_exp = None
            to_exp = None
            is_present = 0

            for l in [*data2["Experience"][k]]:
                if l.strip().startswith("Org"):
                    organisation.append(data2["Experience"][k][l])
                else:
                    if l.strip().startswith("Cli"):
                        organisation.append(data2["Experience"][k][l])
                if l.strip().startswith("Des"):
                    designation.append(data2["Experience"][k][l])
                if l.strip().startswith("Rol"):

                    temp_roles = data2["Experience"][k][l]
                    temp_str = ""
                    for z in range(0, len(temp_roles)):
                        if len(temp_roles[z]) == 0:
                            continue
                        else:
                            temp_str += temp_roles[z] + "\n"

                    work_role.append(temp_str)
                    del temp_roles, temp_str

                if l.strip().startswith("Skills"):
                    work_skill = (", ").join(data2["Experience"][k][l])

                if l.strip().startswith("Sta"):
                    from_exp = data2["Experience"][k][l]
                    # from_exp=start_date

                if l.strip().startswith("End"):
                    if data2["Experience"][k][l] == "Till Date":
                        is_present = 1
                    else:
                        to_exp = data2["Experience"][k][l]
                        # to_exp.append(end_date)

                if l.strip().startswith("Lo"):
                    work_location.append(data2["Experience"][k][l])
            if len(organisation) > 0:
                organisation = organisation
            else:
                organisation = [""]
            if len(designation) > 0:
                designation = designation
            else:
                designation = [""]

            if len(work_location) > 0:
                work_location = work_location
            else:
                work_location = [""]
            if len(work_skill) > 0:
                work_skill = [work_skill]
            else:
                work_skill = [""]
            if len(work_role) > 0:
                work_role = work_role
            else:
                work_role = [""]

            Experiences.objects.create(
                application_id_id=application_id,
                organisations=organisation[0],
                designation=designation[0],
                work_location=work_location[0],
                work_tools=work_skill[0],
                work_role=work_role[0],
                from_exp=from_exp,
                is_present=is_present,
                to_exp=to_exp,
            )

    except:
        pass

    ##_______________________________Skills_______________________________________________________#

    try:

        Skills.objects.create(
            application_id_id=application_id,
            tech_skill=str(set(data2["Technical Skills"]))
            .replace("{", "")
            .replace("'", "")
            .replace("}", "")
            .replace("set()", ""),
        )

    except:
        pass
    try:
        work_tools = (
            Experiences.objects.filter(application_id_id=application_id)
            .values_list("work_tools", flat=True)
            .distinct()
        )
        work_tools1 = (
            Projects.objects.filter(application_id_id=application_id)
            .values_list("work_proj_skills", flat=True)
            .distinct()
        )
        try:
            skills = Skills.objects.get(application_id_id=application_id).tech_skill
            total_skill = list(work_tools) + list(work_tools1) + skills.split(",")
        except:
            total_skill = list(work_tools) + list(work_tools1)
        sot_skills = [re.split("(\d\).\s)", a) for a in total_skill]
        total_skill = [
            item.strip().upper() for sublist in sot_skills for item in sublist
        ]
        total_skill = [t for t in total_skill if not re.match(r"\d\).", t)]
        total_skill = [t for t in total_skill if len(t) > 0]
        total_skill = [i.split(",") for i in total_skill]
        total_skill = [item for sublist in total_skill for item in sublist]
        total_skill = [i.strip() for i in total_skill]
        total_skill = list(dict.fromkeys(total_skill))
        skill_list = ",".join(total_skill)
        if Skills.objects.filter(application_id_id=application_id).exists():
            Skills.objects.filter(application_id_id=application_id).update(
                tech_skill=skill_list
            )
        else:
            Skills.objects.create(
                application_id_id=application_id, tech_skill=skill_list
            )

    except:
        pass
    return redirect("application:pre_preview")
    # except:
    # 	messages.warning(request, 'Upload valid file or contact our support team')
    # 	return redirect('application:personal_info')


# This function for update the candidate personal information details
@login_required
@candidate_required
def Update_Personal_Info(request):

    user_id = request.user
    application_id = Personal_Info.objects.get(user_id=user_id).application_id
    application_status = User_Info.objects.get(user_id=user_id).application_status
    emp_id = User_Info.objects.get(user_id=user_id).employer_id
    if request.method == "POST":
        temp = Personal_Info.objects.filter(user_id=user_id).first()
        temp1 = Additional_Details.objects.filter(
            application_id_id=application_id
        ).first()
        form = Personal_Info_Form(request.POST, instance=temp)
        form2 = Additional_Details_Form(request.POST, instance=temp1)
        if form.is_valid() and form2.is_valid():
            username = request.user
            temp = form.save(commit=False)
            temp.user_id = User.objects.get(username=request.user.username)
            temp.save()
            temp2 = form2.save(commit=False)
            temp2.save()
            user = User.objects.get(username=request.user.username)
            user.first_name = temp.firstname
            user.last_name = temp.lastname
            user.save()
            employer_pool.objects.filter(
                client_id_id=emp_id, candidate_id=temp.application_id
            ).update(
                contact=temp.contact_no,
                linkedin_url=temp.linkedin_url,
                work_exp=temp2.total_exp_year,
                first_name=temp.firstname,
                last_name=temp.lastname,
                email=temp.email,
            )

            return redirect("/application/edit/?about")

    else:
        temp_dummy = Personal_Info.objects.filter(user_id=user_id).values(
            "current_country", "current_state", "current_city"
        )
        temp2 = Personal_Info.objects.filter(user_id=user_id).values()
        temp = Personal_Info.objects.filter(user_id=user_id).first()
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        temp2 = Additional_Details.objects.filter(
            application_id_id=application_id
        ).first()
        form = Personal_Info_Form(instance=temp)
        form2 = Additional_Details_Form(instance=temp2)

    return render(
        request, "application/update_per_info.html", {"form": form, "form2": form2}
    )


# This calss for create the candidate Experience details
class ExperiencesCreateView(BSModalCreateView):
    model = Experiences
    template_name = "application/create_exp.html"
    form_class = Experiences_Form
    success_message = ""
    success_url = reverse_lazy("application:experience_list")

    def get(self, request):
        user_id = self.request.user.id
        application_status = User_Info.objects.get(
            user_id_id=user_id
        ).application_status
        form = Experiences_Form()
        till_date = 0
        is_present = Experiences.objects.filter(
            application_id_id__user_id_id=user_id, is_present=1
        ).order_by("exp_id")
        if is_present.count() > 1:
            till_date = is_present.values("exp_id")[0]["exp_id"]
        context = {
            "form": form,
            "application_status": application_status,
            "till_date": json.dumps(till_date, cls=DjangoJSONEncoder),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_id = self.request.user.id
        application_id = Personal_Info.objects.get(user_id_id=user_id).application_id
        if "organisations" in request.POST:
            if "to_exp" in request.POST:
                Experiences.objects.create(
                    application_id_id=application_id,
                    organisations=request.POST["organisations"],
                    org_domain=request.POST["org_domain"],
                    designation=request.POST["designation"],
                    work_location=request.POST["work_location"],
                    work_tools=request.POST["work_tools"],
                    work_role=request.POST["work_role"],
                    from_exp=request.POST["from_exp"],
                    is_present=0,
                    to_exp=request.POST["to_exp"],
                )
            else:
                Experiences.objects.create(
                    application_id_id=application_id,
                    organisations=request.POST["organisations"],
                    org_domain=request.POST["org_domain"],
                    designation=request.POST["designation"],
                    work_location=request.POST["work_location"],
                    work_tools=request.POST["work_tools"],
                    work_role=request.POST["work_role"],
                    from_exp=request.POST["from_exp"],
                    is_present=1,
                    to_exp=None,
                )
        if "organisations1" in request.POST:
            if "to_exp" in request.POST:
                Experiences.objects.create(
                    application_id_id=application_id,
                    organisations=request.POST["organisations1"],
                    org_domain=request.POST["org_domain1"],
                    designation=request.POST["designation1"],
                    work_location=request.POST["work_location1"],
                    work_tools=request.POST["work_tools1"],
                    work_role=request.POST["work_role1"],
                    from_exp=request.POST["from_exp1"],
                    is_present=0,
                    to_exp=request.POST["to_exp1"],
                )
            else:
                Experiences.objects.create(
                    application_id_id=application_id,
                    organisations=request.POST["organisations1"],
                    org_domain=request.POST["org_domain1"],
                    designation=request.POST["designation1"],
                    work_location=request.POST["work_location1"],
                    work_tools=request.POST["work_tools1"],
                    work_role=request.POST["work_role1"],
                    from_exp=request.POST["from_exp1"],
                    is_present=1,
                    to_exp=None,
                )

        # work_tools = Projects.objects.filter(application_id_id = application_id).values_list('work_proj_skills',flat=True).distinct()
        work_tools = (
            Experiences.objects.filter(application_id_id=application_id)
            .values_list("work_tools", flat=True)
            .distinct()
        )
        try:
            skills = Skills.objects.get(application_id_id=application_id).tech_skill
            total_skill = list(work_tools) + skills.split(",")
        except:
            skills = ""
            total_skill = list(work_tools)
        sot_skills = [re.split("(\d\).\s)", a) for a in total_skill]
        total_skill = [
            item.strip().upper() for sublist in sot_skills for item in sublist
        ]
        total_skill = [t.strip() for t in total_skill if not re.match(r"\d\).", t)]
        total_skill = [t.strip() for t in total_skill if len(t) > 0]
        total_skill = [i.split(",") for i in total_skill]
        total_skill = [item for sublist in total_skill for item in sublist]
        total_skill = list(set(total_skill))
        skill_list = ",".join(total_skill)
        if Skills.objects.filter(application_id_id=application_id).exists():
            Skills.objects.filter(application_id_id=application_id).update(
                tech_skill=skill_list
            )
        else:
            Skills.objects.create(
                application_id_id=application_id, tech_skill=skill_list
            )

        # update_skill_match(application_id)
        return redirect("/application/edit/?experience")


# This calss for update the candidate Experience details
class ExperiencesUpdateView(BSModalUpdateView):
    model = Experiences
    template_name = "application/update_exp.html"
    form_class = Experiences_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def get(self, request, pk, *args, **kwargs):
        code = get_object_or_404(Experiences, pk=pk)
        form = Experiences_Form(instance=code)
        user_info = User_Info.objects.get(user_id=self.request.user).application_status
        till_date = 0
        is_present = Experiences.objects.filter(
            application_id_id__user_id_id=self.request.user.id, is_present=1
        ).order_by("exp_id")
        if is_present.count() > 1:
            till_date = is_present.values("exp_id")[0]["exp_id"]
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "till_date": json.dumps(till_date, cls=DjangoJSONEncoder),
                "app_status": json.dumps(user_info, cls=DjangoJSONEncoder),
            },
        )

    def form_valid(self, form):
        form.save()

        user_id = self.request.user.id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        work_tools = (
            Experiences.objects.filter(application_id_id=application_id)
            .values_list("work_tools", flat=True)
            .distinct()
        )
        try:
            skills = Skills.objects.get(application_id_id=application_id).tech_skill
            total_skill = list(work_tools) + skills.split(",")
        except:
            skills = ""
            total_skill = list(work_tools)
        sot_skills = [re.split("(\d\).\s)", a) for a in total_skill]
        total_skill = [
            item.strip().upper() for sublist in sot_skills for item in sublist
        ]
        total_skill = [t for t in total_skill if not re.match(r"\d\).", t)]
        total_skill = [t for t in total_skill if len(t) > 0]
        total_skill = [i.split(",") for i in total_skill]
        total_skill = [item for sublist in total_skill for item in sublist]
        total_skill = list(dict.fromkeys(total_skill))
        skill_list = ",".join(total_skill)
        if Skills.objects.filter(application_id_id=application_id).exists():
            Skills.objects.filter(application_id_id=application_id).update(
                tech_skill=skill_list
            )
        else:
            Skills.objects.create(
                application_id_id=application_id, tech_skill=skill_list
            )

        # update_skill_match(application_id)
        return redirect("/application/edit/?experience")


# This calss for delete the candidate Experience details
class ExperiencesDeleteView(BSModalDeleteView):
    model = Experiences
    template_name = "application/delete.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Experiences.objects.filter(exp_id=pk)
        cont.delete()
        return redirect("/application/edit/?experience")


# This calss for create the candidate Fresher details
class FresherCreateView(BSModalCreateView):
    model = Fresher
    form_class = Fresher_Form
    success_message = ""
    template_name = "application/create_fresher.html"
    success_url = reverse_lazy("applicationpre_preview")

    def form_valid(self, form):
        user_id = self.request.user
        # user_id = User.objects.get(username = username)
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        list_req = Fresher.objects.filter(
            intern_org=form.cleaned_data["intern_org"],
            intern_project=form.cleaned_data["intern_project"],
            intern_client=form.cleaned_data["intern_client"],
            intern_proj_describe=form.cleaned_data["intern_proj_describe"],
            intern_role=form.cleaned_data["intern_role"],
            application_id=application_id,
        )
        if not list_req.exists():
            form.instance.application_id = Personal_Info.objects.get(
                application_id=application_id
            )
            form.save()
        return redirect("/application/edit/?project")


# This calss for update the candidate Fresher details
class FresherUpdateView(BSModalUpdateView):
    model = Fresher
    template_name = "application/update_fresher.html"
    form_class = Fresher_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):

        form.save()
        return redirect("/application/edit/?project")


# This calss for delete the candidate Fresher details
class FresherDeleteView(BSModalDeleteView):
    model = Fresher
    template_name = "application/delete_without_sm.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Fresher.objects.filter(id=pk)
        cont.delete()
        return redirect("/application/edit/?project")


# This calss for create the candidate Skills details
class SkillsCreateView(CreateView):
    model = Skills
    fields = ("soft_skill", "tech_skill")
    template_name = "application/create_skill.html"
    success_url = reverse_lazy("application:pre_preview")

    def get(self, request):

        try:
            skill_list = open(base_dir + "/" + "media/skills.csv", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
        skill_list = skill_list.read()
        skill_list = skill_list.split("\n")
        form = Skills_Form()
        context = {
            "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
            "form": form,
        }
        return render(request, self.template_name, context)

    def form_valid(self, form):
        user_id = self.request.user
        # user_id = User.objects.get(username = username)
        application_id = Personal_Info.objects.get(user_id=user_id).application_id

        # form.cleaned_data['tech_skill']=
        if not Skills.objects.filter(
            soft_skill=form.cleaned_data["soft_skill"],
            tech_skill=form.cleaned_data["tech_skill"],
            application_id_id=application_id,
        ).exists():
            form.instance.application_id = Personal_Info.objects.get(
                application_id=application_id
            )
            tech_skill = form.cleaned_data["tech_skill"].upper().split(",")
            tech_skill = [i.strip() for i in tech_skill]
            tech_skill = list(dict.fromkeys(tech_skill))
            form.instance.tech_skill = ",".join(tech_skill)
            form.save()
            # update_skill_match(application_id)
        return redirect("/application/edit/?skill")


# This calss for update the candidate Skills details
class SkillsUpdateView(BSModalUpdateView):
    model = Skills
    template_name = "application/update_skill.html"
    form_class = Skills_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def get(self, request, pk):
        user_id = self.request.user
        # user_id = User.objects.get(username = username)
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        if request.user.is_superuser:
            code = get_object_or_404(Skills, pk=pk)
        else:
            code = get_object_or_404(Skills, pk=pk)
        form = Skills_Form(instance=code)
        try:
            skill_list = open(base_dir + "/" + "media/skills.csv", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
        skill_list = skill_list.read()
        skill_list = skill_list.split("\n")
        skills = Skills.objects.get(application_id_id=application_id).tech_skill
        skill_list = skill_list + skills.upper().split(",")
        skill_list = [i.strip() for i in skill_list]
        skill_list = list(dict.fromkeys(skill_list))
        context = {
            "form": form,
            "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        user_id = self.request.user
        # user_id = User.objects.get(username = username)
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        tech_skill = request.POST["tech_skill"].upper().split(",")
        tech_skill = [i.strip() for i in tech_skill]
        tech_skill = list(dict.fromkeys(tech_skill))
        tech_skill = ",".join(tech_skill)
        employer_pool.objects.filter(candidate_id=application_id).update(
            skills=tech_skill,
        )
        Skills.objects.filter(id=pk).update(
            soft_skill=request.POST["soft_skill"], tech_skill=tech_skill
        )
        return redirect("/application/edit/?skill")


# This calss for delete the candidate Skills details
class SkillsDeleteView(BSModalDeleteView):
    model = Skills
    template_name = "application/delete.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Skills.objects.filter(id=pk)
        cont.delete()
        return redirect("/application/edit/?skill")


# This calss for create the candidate Additional Details details
# class AdditionalDetailsCreateView(CreateView):
# 	model = Additional_Details
# 	fields = ('total_exp_year','total_exp_month')
# 	template_name = 'application/create_add.html'
# 	success_url = reverse_lazy('application:pre_preview')

# 	def form_valid(self,form):
# 		username = self.request.user
# 		user_id = User.objects.get(username = username).id
# 		application_id = Personal_Info.objects.get(user_id = user_id).application_id
# 		list_req =Additional_Details.objects.filter(total_exp_year=form.cleaned_data['total_exp_year'],total_exp_month=form.cleaned_data['total_exp_month'],application_id = application_id)
# 		if not list_req.exists():
# 			form.instance.application_id = Personal_Info.objects.get(application_id = application_id)
# 			form.save()
# 		return redirect('application:pre_preview')


# #This calss for update the candidate Additional Details details
# class AdditionalUpdateView(BSModalUpdateView):
# 	model = Additional_Details
# 	template_name = 'application/update_add.html'
# 	form_class = Additional_Details_Form
# 	success_message = ''

# 	success_url = reverse_lazy('application:pre_preview')

# #This calss for delete the candidate Additional Details details
# class AdditionalDeleteView(BSModalDeleteView):
# 	model = Additional_Details
# 	template_name = 'application/delete.html'
# 	success_message = ''
# 	success_url = reverse_lazy('application:pre_preview')


# This calss for create the candidate Education details
class EducationCreateView(BSModalCreateView):
    model = Education
    template_name = "application/create_edu.html"
    form_class = Education_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):

        user_id = self.request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        list_req = Education.objects.filter(
            qual_title=form.cleaned_data["qual_title"],
            qual_spec=form.cleaned_data["qual_spec"],
            institute_name=form.cleaned_data["institute_name"],
            institute_location=form.cleaned_data["institute_location"],
            year_completed=form.cleaned_data["year_completed"],
            application_id=application_id,
        )
        if not list_req.exists():
            form.instance.application_id = Personal_Info.objects.get(
                application_id=application_id
            )
            form.save()
        return redirect("/application/edit/?education")


# This calss for update the candidate Education details
class EducationUpdateView(BSModalUpdateView):
    model = Education
    template_name = "application/update_edu.html"
    form_class = Education_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):

        form.save()
        return redirect("/application/edit/?education")


# This calss for delete the candidate Education details
class EducationDeleteView(BSModalDeleteView):
    model = Education
    template_name = "application/delete_without_sm.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Education.objects.filter(edu_id=pk)
        cont.delete()
        return redirect("/application/edit/?education")


# This calss for create the candidate Certification and Course details
class CertificationCreateView(BSModalCreateView):
    model = Certification_Course
    form_class = Certification_Course_Form
    success_message = ""
    template_name = "application/create_cert.html"
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):
        user_id = self.request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        if not Certification_Course.objects.filter(
            certificate_name=form.cleaned_data["certificate_name"],
            certificate_year=form.cleaned_data["certificate_year"],
            application_id=application_id,
        ).exists():
            form.instance.application_id = Personal_Info.objects.get(
                application_id=application_id
            )
            form.save()
        return redirect("/application/edit/?education")


# This calss for update the candidate Certification and Course details
class CertificationUpdateView(BSModalUpdateView):
    model = Certification_Course
    template_name = "application/update_cert.html"
    form_class = Certification_Course_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):

        form.save()
        return redirect("/application/edit/?education")


# This calss for delete the candidate Certification and Course details
class CertificationDeleteView(BSModalDeleteView):
    model = Certification_Course
    template_name = "application/delete_without_sm.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Certification_Course.objects.filter(id=pk)
        cont.delete()
        return redirect("/application/edit/?education")


# This calss for create the candidate Project details
class ProjectCreateView(CreateView):
    model = Projects
    form_class = Projects_Form
    template_name = "application/create_pro.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def get(self, request):
        user_id = self.request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        form = Projects_Form(application_id=application_id)
        application_status = User_Info.objects.get(user_id=user_id).application_status
        orgs1 = Experiences.objects.filter(application_id_id=application_id).values(
            "organisations", "exp_id", "designation"
        )
        orgs = []
        for i in orgs1:
            if len(i["organisations"]) > 0 and len(i["designation"]) > 0:
                orgs.append((i["exp_id"], i["organisations"] + "-" + i["designation"]))
            elif len(i["designation"]) == 0 and len(i["organisations"]) > 0:
                orgs.append((i["exp_id"], i["organisations"]))
            else:
                pass
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "orgs": json.dumps(orgs, cls=DjangoJSONEncoder),
                "application_status": application_status,
            },
        )

    def post(self, request):
        user_id = self.request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        form = Projects_Form(application_id=application_id)
        orgs1 = Experiences.objects.filter(application_id_id=application_id).values(
            "organisations", "exp_id", "designation"
        )
        orgs = []
        for i in orgs1:
            if len(i["organisations"]) > 0 and len(i["designation"]) > 0:
                orgs.append(
                    (i["exp_id"], i["organisations"] + " - " + i["designation"])
                )
            elif len(i["designation"]) == 0 and len(i["organisations"]) > 0:
                orgs.append((i["exp_id"], i["organisations"]))
            else:
                pass
        for i in range(0, len(request.POST.getlist("work_proj_desig"))):
            try:
                if request.POST.getlist("work_proj_type")[i]:
                    work_proj_type = True
            except:
                work_proj_type = False
            work_id = request.POST.getlist("work_proj_org_id")[i]
            if work_id == "0":
                work_id = None
            Projects.objects.create(
                application_id_id=application_id,
                work_proj_name=request.POST.getlist("work_proj_name")[i],
                work_proj_client=request.POST.getlist("work_proj_client")[i],
                work_proj_describe=request.POST.getlist("work_proj_describe")[i],
                work_proj_desig=request.POST.getlist("work_proj_desig")[i],
                work_proj_role=request.POST.getlist("work_proj_role")[i],
                work_proj_duration=request.POST.getlist("work_proj_duration")[i],
                work_proj_domain=request.POST.getlist("work_proj_domain")[i],
                work_proj_location=request.POST.getlist("work_proj_location")[i],
                work_proj_skills=request.POST.getlist("work_proj_skills")[i],
                work_proj_type=work_proj_type,
                work_proj_org_id_id=work_id,
            )

        for i in range(0, len(request.POST.getlist("work_proj_desig1"))):
            try:
                if request.POST.getlist("work_proj_type1")[i]:
                    work_proj_type = True
            except:
                work_proj_type = False
            work_id = request.POST.getlist("work_proj_org_id1")[i]
            if work_id == "0":
                work_id = None
            Projects.objects.create(
                application_id_id=application_id,
                work_proj_name=request.POST.getlist("work_proj_name1")[i],
                work_proj_client=request.POST.getlist("work_proj_client1")[i],
                work_proj_describe=request.POST.getlist("work_proj_describe1")[i],
                work_proj_desig=request.POST.getlist("work_proj_desig1")[i],
                work_proj_role=request.POST.getlist("work_proj_role1")[i],
                work_proj_duration=request.POST.getlist("work_proj_duration1")[i],
                work_proj_domain=request.POST.getlist("work_proj_domain1")[i],
                work_proj_location=request.POST.getlist("work_proj_location1")[i],
                work_proj_skills=request.POST.getlist("work_proj_skills1")[i],
                work_proj_type=work_proj_type,
                work_proj_org_id_id=work_id,
            )

        work_tools = (
            Projects.objects.filter(application_id_id=application_id)
            .values_list("work_proj_skills", flat=True)
            .distinct()
        )
        # work_tools = Experiences.objects.filter(application_id_id = application_id).values_list('work_tools',flat=True).distinct()
        try:
            skills = Skills.objects.get(application_id_id=application_id).tech_skill
            total_skill = list(work_tools) + skills.split(",")
        except:
            skills = ""
            total_skill = list(work_tools)
        sot_skills = [re.split("(\d\).\s)", a) for a in total_skill]
        total_skill = [
            item.strip().upper() for sublist in sot_skills for item in sublist
        ]
        total_skill = [t for t in total_skill if not re.match(r"\d\).", t)]
        total_skill = [t for t in total_skill if len(t) > 0]
        total_skill = [i.split(",") for i in total_skill]
        total_skill = [item for sublist in total_skill for item in sublist]
        total_skill = list(dict.fromkeys(total_skill))
        skill_list = ",".join(total_skill)
        if Skills.objects.filter(application_id_id=application_id).exists():
            Skills.objects.filter(application_id_id=application_id).update(
                tech_skill=skill_list
            )
        else:
            Skills.objects.create(
                application_id_id=application_id, tech_skill=skill_list
            )

        # update_skill_match(application_id)

        return redirect("/application/edit/?project")


# This calss for update the candidate Project details
def ProjectUpdateView(request, pk, template_name="application/update_pro.html"):
    if request.user.is_superuser:
        code = get_object_or_404(Projects, pk=pk)
    else:
        code = get_object_or_404(Projects, pk=pk)
    if request.method == "POST":
        try:
            if request.POST["work_proj_type"]:
                work_proj_type = True
        except:
            work_proj_type = False
        user_id = request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        form = Projects_Form(
            request.POST or None, instance=code, application_id=application_id
        )
        try:
            Projects.objects.filter(pk=pk).update(
                work_proj_name=request.POST["work_proj_name"],
                work_proj_client=request.POST["work_proj_client"],
                work_proj_describe=request.POST["work_proj_describe"],
                work_proj_desig=request.POST["work_proj_desig"],
                work_proj_role=request.POST["work_proj_role"],
                work_proj_duration=request.POST["work_proj_duration"],
                work_proj_domain=request.POST["work_proj_domain"],
                work_proj_location=request.POST["work_proj_location"],
                work_proj_skills=request.POST["work_proj_skills"],
                work_proj_type=work_proj_type,
                work_proj_org_id_id=request.POST["work_proj_org_id"],
            )
        except:
            Projects.objects.filter(pk=pk).update(
                work_proj_name=request.POST["work_proj_name"],
                work_proj_client=request.POST["work_proj_client"],
                work_proj_describe=request.POST["work_proj_describe"],
                work_proj_desig=request.POST["work_proj_desig"],
                work_proj_role=request.POST["work_proj_role"],
                work_proj_duration=request.POST["work_proj_duration"],
                work_proj_domain=request.POST["work_proj_domain"],
                work_proj_type=work_proj_type,
                work_proj_location=request.POST["work_proj_location"],
                work_proj_skills=request.POST["work_proj_skills"],
                work_proj_org_id_id=None,
            )
        work_tools = (
            Projects.objects.filter(application_id_id=application_id)
            .values_list("work_proj_skills", flat=True)
            .distinct()
        )
        # work_tools = Experiences.objects.filter(application_id_id = application_id).values_list('work_tools',flat=True).distinct()
        try:
            skills = Skills.objects.get(application_id_id=application_id).tech_skill
            total_skill = list(work_tools) + skills.split(",")
        except:
            skills = ""
            total_skill = list(work_tools)
        sot_skills = [re.split("(\d\).\s)", a) for a in total_skill]
        total_skill = [
            item.strip().upper() for sublist in sot_skills for item in sublist
        ]
        total_skill = [t for t in total_skill if not re.match(r"\d\).", t)]
        total_skill = [t for t in total_skill if len(t) > 0]
        total_skill = [i.split(",") for i in total_skill]
        total_skill = [item for sublist in total_skill for item in sublist]
        total_skill = list(dict.fromkeys(total_skill))
        skill_list = ",".join(total_skill)
        if Skills.objects.filter(application_id_id=application_id).exists():
            Skills.objects.filter(application_id_id=application_id).update(
                tech_skill=skill_list
            )
        else:
            Skills.objects.create(
                application_id_id=application_id, tech_skill=skill_list
            )

        # update_skill_match(application_id)
        return redirect("/application/edit/?project")
    else:
        user_id = request.user
        # user_id = User.objects.get(username = username).id
        user_info = User_Info.objects.get(user_id=user_id).application_status
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        form = Projects_Form(
            request.POST or None, instance=code, application_id=application_id
        )
    return render(
        request,
        template_name,
        {"form": form, "app_status": json.dumps(user_info, cls=DjangoJSONEncoder)},
    )


# This calss for delete the candidate Project details
class ProjectDeleteView(BSModalDeleteView):
    model = Projects
    template_name = "application/delete.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):

        cont = Projects.objects.filter(project_id=pk)
        cont.delete()
        return redirect("/application/edit/?project")


# This calss for create the candidate Contributions details
class ContributionsCreateView(BSModalCreateView):
    model = Contributions
    template_name = "application/create_cont.html"
    form_class = Contributions_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):
        user_id = self.request.user
        # user_id = User.objects.get(username = username).id
        application_id = Personal_Info.objects.get(user_id=user_id).application_id
        list_req = Contributions.objects.filter(
            contrib_text=form.cleaned_data["contrib_text"],
            contrib_type=form.cleaned_data["contrib_type"],
            application_id=application_id,
        )
        if not list_req.exists():
            form.instance.application_id = Personal_Info.objects.get(
                application_id=application_id
            )
            form.save()
        return redirect("/application/edit/?contribution")


# This calss for update the candidate Contributions details
class ContributionsUpdateView(BSModalUpdateView):
    model = Contributions
    template_name = "application/update_cont.html"
    form_class = Contributions_Form
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def form_valid(self, form):
        form.save()
        return redirect("/application/edit/?contribution")


# This calss for delete the candidate Contributions details
class ContributionsDeleteView(BSModalDeleteView):
    model = Contributions
    template_name = "application/delete_without_sm.html"
    success_message = ""
    success_url = reverse_lazy("application:pre_preview")

    def post(self, request, pk, *args, **kwargs):
        cont = Contributions.objects.filter(contributions_id=pk)
        cont.delete()
        return redirect("/application/edit/?contribution")


# This Function for personal info country state and city dropdown
def load_states(request):
    if request.GET.get("country") != None:
        country_id = request.GET.get("country")
        if country_id == "":
            country_id = None
        states = State.objects.filter(country_id=country_id).order_by("name")
        return render(
            request, "application/city_dropdown_list_options.html", {"states": states}
        )
    else:
        state_id = request.GET.get("state")
        if state_id == "":
            state_id = None
        city = City.objects.filter(state_id=state_id).order_by("name")
        return render(
            request, "application/city_dropdown_list_options1.html", {"city": city}
        )


# Reprofilng function
def re_profiling(request):
    user_id = request.user
    # logger.info('re_profiling Happen for ------'+ str(username))
    # user_id = User.objects.get(username = username).id
    user_info = User_Info.objects.get(user_id=user_id)
    application_id = Personal_Info.objects.get(user_id=user_id).application_id

    try:
        sentences_list = request.GET["exp_list"]
    except:
        sentences_list = None

    # Profiling function started
    profiles, recommended_roles, cl_result = profiling(application_id, sentences_list)

    if "preview_button" in request.POST:
        if user_info.application_status == 100:
            return redirect("profile_list", username=user_id.username)
        else:
            if profiles != 0:
                if Visualize.objects.filter(application_id_id=application_id).exists():
                    Visualize.objects.filter(application_id_id=application_id).delete()
                    Visualize_instance = Visualize.objects.create(
                        application_id_id=application_id,
                        business_intelligence=profiles["Business_Intelligence"],
                        data_analysis=profiles["Data_Analysis"],
                        data_engineering=profiles["Data_Engineering"],
                        devops=profiles["Dev_Ops"],
                        machine_learning=profiles["Machine_Learning"],
                        others=profiles["others"],
                        is_reprofiled=1,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )
                else:
                    Visualize_instance = Visualize.objects.create(
                        application_id_id=application_id,
                        business_intelligence=profiles["Business_Intelligence"],
                        data_analysis=profiles["Data_Analysis"],
                        data_engineering=profiles["Data_Engineering"],
                        devops=profiles["Dev_Ops"],
                        machine_learning=profiles["Machine_Learning"],
                        others=profiles["others"],
                        is_reprofiled=0,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )

        if len(recommended_roles) > 0:
            username = request.user
            user_info = User_Info.objects.get(user_id=username)
            user_info.ds_profile_id = 1
            if Recommended_Role.objects.filter(
                application_id_id=application_id
            ).exists():
                Recommended_Role.objects.filter(
                    application_id_id=application_id
                ).delete()
            for i in recommended_roles:
                recom_role_id = tmeta_ds_main_roles.objects.get(tag_name=i).id
                Recommended_Role.objects.create(
                    user_id_id=request.user.id,
                    application_id_id=application_id,
                    recommended_role_id=recom_role_id,
                )
                user_info.selected_role_id = recom_role_id
            user_info.application_status = 100
            user_info.val_status_2recruiter = 0
            user_info.save()

        return redirect("profile_list", username=username.username)

    if "exp_list" in request.GET:
        user_info = User_Info.objects.get(user_id_id=user_id)
        user_info.application_status = 90
        user_info.save()
    if profiles == 0:

        messages.warning(
            request,
            "The profiling request could not be completed due to server error, Please try again later",
        )

    role = Recommended_Role.objects.filter(application_id=application_id)
    role = role.annotate(
        role=Subquery(
            tmeta_ds_main_roles.objects.filter(id=OuterRef("recommended_role"))[
                :1
            ].values("tag_name")
        )
    )
    recommended_role = role.values_list("role", flat=True)
    a = set(recommended_role)
    b = set(recommended_roles)

    if a == b:
        same_role = 1
    else:
        same_role = 0
    context = {
        "profiles": json.dumps(profiles, cls=DjangoJSONEncoder),
        "recommended_role": recommended_role,
        "rec_role": recommended_roles,
        "same_role": same_role,
        "recommended_roles": json.dumps(recommended_roles, cls=DjangoJSONEncoder),
    }

    return render(request, "application/re_profiling.html", context)


# uload resume function
@never_cache
def upload_resume(request):
    if request.user.is_staff == True:
        logout(request)
    if request.method == "GET":
        if request.user.is_authenticated:
            if request.user.email == None or request.user.email == "":
                logout(request)
            if request.user.is_staff == True:
                logout(request)
            try:
                user_info = User_Info.objects.get(user_id=request.user)
                if user_info.active == 1:
                    return redirect("application:dashboard")
            except User_Info.DoesNotExist:
                user_info = None
            except Exception as e:
                logger.error("Error in the user_info table -----" + str(e))
                user_info = None

    if request.method == "POST":
        if not request.user.is_authenticated:
            username = generate_random_username()
            password = generate_random_username(split=8)
            user = User.objects.create(username=username, date_joined=datetime.now())
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
        form_upload = Upload_resume(request.POST, request.FILES)
        if form_upload.is_valid():
            logger.info("form_upload is valid")
            temp = form_upload.save(commit=False)
            temp.upload_id = User.objects.get(username=request.user)
            temp.save()
            filepath = form_upload.instance.resume_file.path
            file_name = os.path.splitext(os.path.basename(filepath))
            global filename
            filename = "".join(list(file_name))
            s_time = datetime.now()
            sentences_list = parsing(filename)
            sentences_list = ast.literal_eval(sentences_list)
            for a in sentences_list:
                resume_data_upload = IL_RP_Output()
                resume_data_upload.user_id_id = User.objects.get(
                    username=request.user
                ).id
                resume_data_upload.predicted_sentence = a[0]
                resume_data_upload.model_name = a[1]
                resume_data_upload.entity_text = a[2]
                resume_data_upload.entity_label = a[3]
                resume_data_upload.save()
            if not User_Info.objects.filter(user_id=request.user).exists():
                if "email" in request.GET:
                    request.session["invites"] = 0
                    User_Info.objects.create(
                        user_id=request.user,
                        username=request.user.username,
                        password=password,
                        employer_id=request.GET["emp-id"],
                        email=request.GET["email"],
                        active=True,
                    )
                    User.objects.filter(username=request.user).update(
                        email=request.GET["email"], is_active=True
                    )
                elif "emp-id" in request.GET:
                    request.session["invites"] = 1
                    User_Info.objects.create(
                        user_id=request.user,
                        username=request.user.username,
                        employer_id=request.GET["emp-id"],
                        password=password,
                    )
                else:
                    request.session["invites"] = 1
                    User_Info.objects.create(
                        user_id=request.user,
                        username=request.user.username,
                        password=password,
                    )
                personal = Personal_Info.objects.create(user_id=request.user)
                Additional_Details.objects.create(
                    application_id=personal,
                    total_exp_year=0,
                    total_exp_month=0,
                )

            else:
                if Personal_Info.objects.filter(
                    user_id=request.user,
                ).exists():
                    personal = Personal_Info.objects.get(user_id=request.user)
                else:
                    personal = Personal_Info.objects.create(
                        user_id=request.user,
                        firstname=request.user.first_name,
                        lastname=request.user.last_name,
                        linkedin_url="https://",
                        email=request.user.email,
                    )
                    Additional_Details.objects.create(
                        application_id=personal,
                        total_exp_year=0,
                        total_exp_month=0,
                    )
            return redirect("application:pre_population")
        if request.POST["resume_file"] == "":

            if not User_Info.objects.filter(user_id=request.user).exists():
                User_Info.objects.create(
                    user_id=request.user,
                    username=request.user.username,
                    password=password,
                    employer_id=request.GET["emp-id"],
                )
                personal = Personal_Info.objects.create(user_id=request.user)
            else:
                if Personal_Info.objects.filter(user_id=request.user).exists():
                    return redirect("application:pre_preview")
                else:
                    personal = Personal_Info.objects.create(
                        user_id=request.user,
                        firstname=request.user.first_name,
                        lastname=request.user.last_name,
                        linkedin_url="https://",
                        email=request.user.email,
                    )
            Additional_Details.objects.create(
                application_id=personal,
                total_exp_year=0,
                total_exp_month=0,
            )
            return redirect("application:pre_preview")
    resume = Upload_resume()

    context = {"resume": resume}

    response = render(request, "upload_resume.html", context)

    return response


# Random username and password creation
def generate_random_username(
    length=8, chars=ascii_lowercase + digits, split=4, delimiter="_"
):

    username = "".join([choice(chars) for i in range(length)])

    if split:
        username = delimiter.join(
            [
                username[start : start + split]
                for start in range(0, len(username), split)
            ]
        )

    try:
        User.objects.get(username=username)
        return generate_random_username(
            length=length, chars=chars, split=split, delimiter=delimiter
        )
    except User.DoesNotExist:
        return username


# Default basic info popup function
def basic_detail(request, template_name="application/basic_detail.html"):
    applicant_details = Personal_Info.objects.get(user_id=request.user)
    user_info = User_Info.objects.get(user_id=request.user)
    add_details = Additional_Details.objects.get(application_id=applicant_details)
    user_valid = 0
    if user_info.active == True:
        applicant_details.email = User.objects.get(username=request.user).email
        applicant_details.save()
        user_valid = 1
        form = basic_detail_Form(instance=applicant_details)
        # form.fields['email'].disabled = True
        exp_form = Additional_Details_Form(instance=add_details)
    else:
        form = basic_detail_Form(instance=applicant_details)
        exp_form = Additional_Details_Form(instance=add_details)

    if request.method == "POST":
        form = basic_detail_Form(request.POST, instance=applicant_details)
        exp_form = Additional_Details_Form(request.POST, instance=add_details)
        if form.is_valid() and exp_form.is_valid():
            temp = form.save(commit=False)
            exp_form = exp_form.save(commit=False)
            temp.save()
            exp_form.save()
            user_info.first_name = request.POST["firstname"]
            user_info.last_name = request.POST["lastname"]
            user_info.email = request.POST["email"]
            user_info.application_id = applicant_details
            user_info.save()
            User.objects.filter(id=request.user.id).update(
                first_name=request.POST["firstname"],
                last_name=request.POST["lastname"],
                email=request.POST["email"],
            )
            try:
                if request.session["email"] == 1:
                    if user_info.active == True:
                        request.session["email"] = 2
                    else:
                        request.session["email"] = 0
            except KeyError:
                if user_info.active == True:
                    request.session["email"] = 2
                else:
                    request.session["email"] = 0
            try:
                emp_id_cookies = request.COOKIES["emp-id"]
            except:
                emp_id_cookies = User_Info.objects.get(user_id=request.user).employer_id
            company_name = company_details.objects.get(
                recruiter_id_id=emp_id_cookies
            ).company_name
            if (
                user_info.active != True
                and employer_pool.objects.filter(
                    client_id_id=emp_id_cookies, email=request.POST["email"]
                ).exists()
                == False
            ):
                request.session["OTP"] = generate_random_username(chars=digits, split=8)
                current_site = get_current_site(request)

                # request.session['email'] = 0
                mail_notification(
                    request.user,
                    "verify_otp_email.html",
                    "Secure One-Time-Password for email verification",
                    domain=current_site,
                    code=request.session["OTP"],
                    company_name=company_name,
                )
            else:
                request.session["OTP"] = 0
                request.session["email"] = 2
                emp_id = User_Info.objects.get(user_id=request.user).employer_id
                return_url = 1
                if emp_id == None:
                    emp_id = emp_id_cookies
                    user_info.employer_id = emp_id_cookies
                    user_info.save()
                    return_url = 0
                applicant_details = Personal_Info.objects.get(user_id=request.user)
                try:
                    skills = Skills.objects.get(application_id=applicant_details)
                    try:
                        skilld = skills.tech_skill + "," + skills.soft_skill
                    except:
                        skilld = skills.tech_skill
                except:
                    skilld = ""
                location = str(
                    applicant_details.current_city.name
                    + ", "
                    + applicant_details.current_state.name
                    + ", "
                    + applicant_details.current_country.name
                )

                if employer_pool.objects.filter(
                    client_id_id=emp_id, email=applicant_details.email
                ).exists():
                    employer_pool.objects.filter(
                        client_id_id=emp_id, email=applicant_details.email
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
                        exp_salary=applicant_details.exp_gross,
                        skills=skilld,
                        location=location,
                    )
                else:
                    employer_pool.objects.create(
                        client_id_id=emp_id,
                        email=applicant_details.email,
                        candidate_id=applicant_details,
                        can_source_id=4,
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
                        exp_salary=applicant_details.exp_gross,
                        skills=skilld,
                        location=location,
                    )
                    avail = client_features_balance.objects.get(
                        client_id_id=emp_id, feature_id_id=12
                    )
                    if not avail.available_count == None:
                        avail.available_count = avail.available_count - 1
                        avail.save()
                    form_upload = Myfiles.objects.filter(upload_id=request.user).last()
                    filepath_str = form_upload.resume_file
                    file_path = str(filepath_str)

                    emp = employer_pool.objects.get(
                        client_id_id=emp_id, email=applicant_details.email
                    )
                    candidate_parsed_details.objects.create(
                        candidate_id=emp,
                        resume_file_path=file_path,
                        parsed_text=" ",
                        resume_description=" ",
                    )
                try:
                    company_name = company_details.objects.get(
                        recruiter_id_id=emp_id
                    ).company_name
                except:
                    company_name = ""
                mail_notification(
                    request.user,
                    "login_email.html",
                    str(company_name) + " Login ",
                    company_name=company_name,
                )
                if user_valid == 0:
                    return redirect("application:pre_preview")
                return redirect("application:dashboard")
            return redirect("application:pre_preview")
    user_id = request.user

    form_upload = Myfiles.objects.filter(upload_id=user_id).order_by("-id")[0]
    filepath_str = form_upload.resume_file
    file_path = str(filepath_str)
    filepath = file_path.split("/")
    filename = filepath[1]
    try:
        json_data = open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json")
    except:
        json_data = open(os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json")

    data = json.load(json_data)
    try:
        form.fields["email"].initial = data["Personal"]["Email"]
    except KeyError:
        pass
    try:
        form.fields["Date_of_birth"].initial = data["Personal"]["Date of Birth"].split(
            "-"
        )[0]
    except KeyError:
        pass
    try:
        form.fields["linkedin_url"].initial = data["Personal"]["LinkedIn"]
    except KeyError:
        form.fields["linkedin_url"].initial = "https://"
    try:
        form.fields["code_repo"].initial = data["Personal"]["Code Repo"]
    except KeyError:
        pass
    context = {"form": form, "exp_form": exp_form, "user_valid": user_valid}
    return render(request, template_name, context)


# OTP verification and resend function
def otp_verification(request):
    data = {}

    # OTP verification function
    if "OTP" in request.GET:
        otp = request.GET["OTP"]
        if otp == request.session["OTP"]:
            request.session["OTP"] = 0
            User_Info.objects.filter(user_id=request.user).update(active=1)
            data["success"] = 1
            request.session["email"] = 2
            jd_id = request.COOKIES["jd-id"]

            emp_id = request.COOKIES["emp-id"]
            applicant_details = Personal_Info.objects.get(user_id=request.user)

            # client_id = JD_form.objects.get(id=emp_id).user_id
            try:
                skills = Skills.objects.get(application_id=applicant_details)
                try:
                    skilld = skills.tech_skill + "," + skills.soft_skill
                except:
                    skilld = skills.tech_skill
            except:
                skilld = ""
            location = str(
                applicant_details.current_city.name
                + ", "
                + applicant_details.current_state.name
                + ", "
                + applicant_details.current_country.name
            )

            if employer_pool.objects.filter(
                client_id_id=emp_id, email=applicant_details.email
            ).exists():
                employer_pool.objects.filter(
                    client_id_id=emp_id, email=applicant_details.email
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
                    exp_salary=applicant_details.exp_gross,
                    skills=skilld,
                    location=location,
                )
            else:
                employer_pool.objects.create(
                    client_id_id=emp_id,
                    email=applicant_details.email,
                    candidate_id=applicant_details,
                    can_source_id=4,
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
                    exp_salary=applicant_details.exp_gross,
                    skills=skilld,
                    location=location,
                )
                avail = client_features_balance.objects.get(
                    client_id_id=emp_id, feature_id_id=12
                )
                if avail.available_count != None:
                    avail.available_count = avail.available_count - 1
                    avail.save()
            form_upload = Myfiles.objects.filter(upload_id=request.user).last()
            filepath_str = form_upload.resume_file
            file_path = str(filepath_str)

            emp = employer_pool.objects.get(
                client_id_id=emp_id, email=applicant_details.email
            )
            candidate_parsed_details.objects.create(
                candidate_id=emp, resume_file_path=file_path, parsed_text=" "
            )
            User_Info.objects.filter(user_id=request.user).update(
                employer_id=int(emp_id)
            )
            try:
                company_name = company_details.objects.get(
                    recruiter_id_id=emp_id
                ).company_name
            except:
                company_name = ""
            mail_notification(
                request.user,
                "login_email.html",
                str(company_name) + " Login ",
                company_name=company_name,
            )
            return JsonResponse(data)
        else:
            data["success"] = 0
            return JsonResponse(data)

    # Resend OTP function
    if "resend" in request.GET:
        request.session["OTP"] = generate_random_username(chars=digits, split=8)
        current_site = get_current_site(request)
        mail_notification(
            request.user,
            "verify_otp_email.html",
            "Secure One-Time-Password for email verification ",
            domain=current_site,
            code=request.session["OTP"],
        )
        data["success"] = 2
        return JsonResponse(data)

    # Change email redirection
    if "change" in request.GET:
        request.session["email"] = 1
        data["success"] = 3
        return JsonResponse(data)


# on the field email validation function
def email_validation(request):
    email = request.GET["email"]
    data = {}
    data["success"] = 0
    emp_id = request.COOKIES["emp-id"]
    if User.objects.filter(email=email).exists():
        if employer_pool.objects.filter(email=email, client_id_id=emp_id).exists():
            data["success"] = 1
    return JsonResponse(data)


@login_required
@candidate_required
def dashboard(request):
    emp_id = User_Info.objects.get(user_id=request.user).employer_id
    can_id = Personal_Info.objects.get(user_id=request.user)
    # try:
    candidate_id = employer_pool.objects.get(client_id_id=emp_id, candidate_id=can_id)
    # except:
    # 	candidate_id = None
    message = Message_non_applicants.objects.filter(
        sender_id=emp_id, receiver=candidate_id
    )
    if message.count() > 0:
        for i in message:
            Message.objects.create(
                sender_id=i.sender.id,
                jd_id=i.jd_id,
                receiver_id=request.user.id,
                text=i.text,
                date_created=i.date_created,
            )
        message.delete()
    applied_job = applicants_status.objects.filter(
        candidate_id=candidate_id, client_id_id=emp_id, status_id__in=[1, 2, 3, 4, 7]
    )
    applied_job = applied_job.annotate(
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "country__name"
            )
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "state__name"
            )
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "city__name"
            )
        ),
    ).order_by("-created_on")
    message_count = Message.objects.filter(
        sender_id=emp_id, receiver_id=request.user.id
    ).exists()
    invites = Candi_invite_to_apply.objects.filter(candidate_id=candidate_id)
    invites = invites.annotate(
        applied=Subquery(
            applied_job.filter(jd_id=OuterRef("jd_id"))[:1].values("candidate_id")
        ),
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "country__name"
            )
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "state__name"
            )
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "city__name"
            )
        ),
    ).order_by("-created_at")
    applied_job = applied_job.annotate(
        invited=Subquery(
            invites.filter(jd_id=OuterRef("jd_id"))[:1].values("candidate_id")
        ),
    )  # for i in invites:
    # 	data['jd_id']= i.jd_id
    # for email in Candi_invite_to_apply.objects.filter(candidate_id=candidate_id).values_list('jd_id', flat=True).distinct():
    #     Email.objects.filter(pk__in=Email.objects.filter(email=email).values_list('id', flat=True)[1:]).delete()
    chatname = str(candidate_id.client_id.id) + "-" + str(request.user.id)
    try:
        company_detail = company_details.objects.get(recruiter_id_id=emp_id)
    except:
        company_detail = None
    try:
        setting = career_page_setting.objects.get(recruiter_id_id=emp_id)
    except:
        setting = None
    context = {
        "applied_job": applied_job,
        "invites": invites,
        "message_count": message_count,
        "chatname": chatname,
        "company_detail": company_detail,
        "setting": setting,
    }
    response = render(request, "application/dashboard.html", context)

    return response


def candidate_message(request, jd_id):
    emp_id = User_Info.objects.get(user_id=request.user).employer_id
    can_id = Personal_Info.objects.get(user_id=request.user)
    try:
        candidate_id = employer_pool.objects.get(
            client_id_id=emp_id, candidate_id=can_id
        )
    except:
        candidate_id = None
    chatname = str(candidate_id.client_id.id) + "-" + str(request.user.id)
    jd = JD_form.objects.get(id=jd_id)
    message_count = Message.objects.filter(
        sender_id=emp_id, receiver_id=request.user.id, jd_id_id=jd_id
    ).exists()
    context = {
        "message_count": message_count,
        "jd": jd,
        "chatname": chatname,
    }
    response = render(request, "application/candidate_message.html", context)

    return response


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def password_change(request):

    password = PasswordChangeForm(request.user)
    emp_id = User_Info.objects.get(user_id=request.user).employer_id
    try:
        company_detail = company_details.objects.get(recruiter_id_id=emp_id)
    except:
        company_detail = None
    try:
        setting = career_page_setting.objects.get(recruiter_id_id=emp_id)
    except:
        setting = None
    if request.method == "POST":
        if "password" in request.POST:
            password = PasswordChangeForm(request.user, request.POST)
            if password.is_valid():
                user = password.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")
                return redirect("application:password_change")
    context = {
        "password": password,
        "company_detail": company_detail,
        "setting": setting,
    }
    response = render(request, "application/password.html", context)
    return response


def qualification_formater(data):
    sentences = []
    for entry in data:
        entry = {k.lower().replace(" ", "_"): v for k, v in entry.items()}
        parts = []
        if "institution" in entry:
            parts.append(f"Attended {entry['institution']}")
        if "university" in entry:
            parts.append(f"Attended {entry['university']}")
        if "degree" in entry:
            if entry["degree"]:
                degree = entry["degree"]
                parts.append(f"earned a {degree}")
        if "degree_obtained" in entry:
            if entry["degree_obtained"]:
                degree = entry["degree_obtained"]
                parts.append(f"earned a {degree}")
        if "major" in entry:
            if entry["major"]:
                parts.append(f"in {entry['major']}")
        if "minor" in entry:
            if entry["minor"]:
                parts.append(f"with a minor in {entry['minor']}")
        graduation_year = (
            entry["graduation_year"].replace("/", "-")
            if entry["graduation_year"]
            else None
        )
        if graduation_year:
            parts.append(f"and graduated in {graduation_year}")
        if entry["university"] or entry["degree"] or entry["degree_obtained"]:
            sentence = " ".join(parts)
            sentences.append(sentence)
    return sentences


def skills_fromater(skills_list):
    lst = []
    for i in skills_list:
        if ":" in i and i != "None" and i:
            i = i.replace(":", ",")
        i = i.splitlines()
        lst.extend(i)
    lst = list(filter(lambda x: x != "None", set(lst)))
    return lst


def skill_updation(resume, app_id):
    tech_skill = resume.get("Technical skills", None)
    soft_skill = resume.get("Soft Skills", None)
    if soft_skill == None:
        soft_skill = resume.get("Soft skills", None)
    filtered_soft = None
    filtered_tech = None
    if tech_skill and tech_skill != "null" and tech_skill != "None":
        filtered_tech = [skill for skill in tech_skill if skill]
        filtered_tech = [
            skill.replace("(", "").replace(")", "") for skill in filtered_tech
        ]
    if (
        soft_skill
        and soft_skill != "null"
        and soft_skill != None
        and soft_skill != "None"
    ):
        filtered_soft = [skill for skill in soft_skill if skill]
        filtered_soft = [
            skill.replace("(", "").replace(")", "") for skill in filtered_soft
        ]
    if filtered_tech or filtered_soft:
        for item in filtered_soft:
            if item in filtered_tech:
                filtered_tech.remove(item)
        filtered_tech = ", ".join(filtered_tech)
        filtered_soft = ", ".join(filtered_soft)
        if Skills.objects.filter(application_id=app_id).exists():
            Skills.objects.filter(application_id=app_id).update(
                tech_skill=filtered_tech, soft_skill=filtered_soft
            )
        else:
            Skills.objects.filter(
                application_id=Personal_Info.objects.get(application_id=app_id)
            ).update(tech_skill=filtered_tech, soft_skill=filtered_soft)
    else:
        Skills.objects.filter(
            application_id=Personal_Info.objects.get(application_id=app_id)
        ).update(tech_skill=filtered_tech, soft_skill=filtered_soft)

    return None


def overview_updation(parsed_resume_json, app_id):
    success = parsed_resume_json.get("Qualifications", None)
    if success:
        if (
            parsed_resume_json["Qualifications"] != []
            and parsed_resume_json["Qualifications"] != None
            and parsed_resume_json["Qualifications"] != ""
            and parsed_resume_json["Qualifications"] != {}
            and parsed_resume_json["Qualifications"] != "[]"
        ):
            try:
                if isinstance(((parsed_resume_json["Qualifications"])[0]), dict):
                    parsed_resume_json["Qualifications"] = qualification_formater(
                        (parsed_resume_json["Qualifications"])
                    )
                if isinstance(((parsed_resume_json["Qualifications"])[0]), str):
                    parsed_resume_json["Qualifications"] = json.loads(
                        parsed_resume_json["Qualifications"]
                    )
                    parsed_resume_json["Qualifications"] = qualification_formater(
                        (parsed_resume_json["Qualifications"])
                    )
            except:
                pass
    success1 = parsed_resume_json.get("Total years of Experience", None)
    if success1 == None:
        success1 = parsed_resume_json.get("Total Years of Experience", None)
    if success1:
        work_exp = None
        if Additional_Details.objects.filter(application_id=app_id).exists():
            exp_year = Additional_Details.objects.get(
                application_id=app_id
            ).total_exp_year
            exp_month = Additional_Details.objects.get(
                application_id=app_id
            ).total_exp_month
            if exp_year != 0 and exp_month != 0:
                work_exp = {"Years": str(exp_year), "Months": str(exp_month)}
            elif exp_year == 0 and exp_month != 0:
                work_exp = {"Years": str(exp_year), "Months": str(exp_month)}
            elif exp_year != 0 and exp_month == 0:
                work_exp = {"Years": str(exp_year)}
            parsed_resume_json["Total years of Experience"] = work_exp
    overview = convert_to_html(parsed_resume_json)
    if overview:
        # if Resume_overview.objects.filter(application_id=app_id).exists():
        #     Resume_overview.objects.filter(application_id=app_id).update(Resume_overview = overview)
        # else:
        if candidate_parsed_details.objects.filter(
            candidate_id__candidate_id=app_id
        ).exists():
            description = candidate_parsed_details.objects.get(
                candidate_id__candidate_id=app_id
            ).resume_description
            if not Resume_overview.objects.filter(application_id=app_id).exists():
                Resume_overview.objects.create(
                    application_id=Personal_Info.objects.get(application_id=app_id),
                    Resume_overview=overview,
                    parsed_resume=json.dumps(parsed_resume_json),
                    resume_description=description,
                )
    overview = ""
    if Resume_overview.objects.filter(application_id=app_id).exists():
        overview = Resume_overview.objects.get(application_id=app_id).Resume_overview
    return overview


def Candidate_creation(can_id):  # IF Employerpool Doesnot Exist()
    if Personal_Info.objects.filter(application_id=can_id.application_id).exists():
        applicant = Personal_Info.objects.get(application_id=can_id.application_id)
        work_exp = None
        exp_year = Additional_Details.objects.get(application_id=can_id).total_exp_year
        exp_month = Additional_Details.objects.get(
            application_id=can_id
        ).total_exp_month
        if exp_year != 0 and exp_month != 0:
            work_exp = str(exp_year) + " Years" + " " + str(exp_month) + " Months"
        elif exp_year == 0 and exp_month != 0:
            work_exp = str(exp_year) + " Years" + " " + str(exp_month) + " Months"
        elif exp_year != 0 and exp_month == 0:
            work_exp = str(exp_year) + " Years"
        applicant_details = Personal_Info.objects.get(
            application_id=can_id.application_id
        )
        candi_source = tmeta_candidate_source.objects.get(id=3)
        user_id = User_Info.objects.get(application_id=can_id).employer_id
        user_id = User.objects.get(id=user_id)
        skills = Skills.objects.get(application_id=can_id)
        try:
            skills = skills.tech_skill + "," + skills.soft_skill
        except:
            skills = skills.tech_skill
        employer_pool.objects.create(
            first_name=applicant.firstname,
            last_name=applicant.lastname,
            email=applicant.email,
            contact=applicant.contact_no,
            linkedin_url=applicant.linkedin_url,
            work_exp=work_exp,
            candidate_id=applicant_details,
            can_source_id=candi_source.id,
            exp_salary=applicant.exp_gross,
            client_id=user_id,
            user_id=user_id,
            skills=skills,
        )
    return True
