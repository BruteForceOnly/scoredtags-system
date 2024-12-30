from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import Avg, F #will need this in the future to increment votes
from django.db.models.functions import Lower #might not need in postgres, but using it for sqlite
from .models import EditRequest, EditRequestComment, Tag, Creator, Project, ProjectSeries, ProjectSeriesEntry, SharedData, OverallProjectScoreBallot
from .forms import AddNewSharedDataForm, AddNewDataNameForm, AddNewProjectSeriesForm, EditProjectDateForm, SubmitProjectOverallScoreBallotForm
import math, unicodedata, hashlib, os
from django.apps import apps
from django.utils import timezone
#FOR TESTING
from django.conf import settings
from django.db import connection
#to check the number of db hits use:
#print(f"test breakpoint: {len(connection.queries)}") #TEST
#and you can render to see the db hits from the templating by passing in "connection": connection


# Create your views here.
def index(request):
    """
    top_search_uid = 0
    top_search_vars = {
        "uid": top_search_uid,
        "placeholder_text": "search...",
        "search_item_type": "project",
    }
    return render(request, "core/index.html", {"top_search_vars": top_search_vars})
    """
    return render(request, "core/index.html")

def under_construction(request):
    return render(request, "core/reusable/under-construction.html")


###############################################################################
# Test Pages
###############################################################################
def test_main(request):
    test_project = Project.objects.get(pk=36)
    test_altnames = list(test_project.shareddata.dataname_set.all()[:0])
    return render(request, "core/test/test-main.html", {"test_altnames": test_altnames})

def test_partial(request):
    return render(request, "core/test/swaps/test-partial.html")

def test_post(request):
    print(request.POST)
    print(request.headers)
    return render(request, "core/test/swaps/test-post.html")
###############################################################################
###############################################################################


###############################################################################
# Universal
###############################################################################
DEFAULT_EDIT_DATE_UI_VARS = {
    "uid": "ed1",
    "my_tr_id": "hidden-rdate-or-ludate-input", #could potentially be something else as well
    "url_endpoint": f"/tags_creators_projects/0/edit-date/",
    "hx_swap_target": "#td_id_for_data_to_be_swapped",
    "message_list_id": "message-list-rdate-or-ludate"
}

DEFAULT_EDIT_SHAREDDATA_TYPE_UI_VARS = {
    "uid": "sdt1",
    "url_endpoint": f"/tags_creators_projects/0/edit-sdtype/",
    "hx_swap_target": "#td_id_for_data_to_be_swapped"
}

DEFAULT_ADD_ALTNAME_BUTTON_VARS = {
    "uid": "altn1",
    "elt_to_show_id": "add-new-item-input-wrapper-altn1",
    "button_text": "+ Add New Name",
    "input_placeholder": "alternative name",
    "input_name": "newaltname",
    "url_endpoint": f"/tags_creators_projects/0/add-altname/",
    "hx_swap_target": "#swappable-altnames-list-data"
}

DEFAULT_ADD_TAG_SEARCH_SELECT_VARS = {
    "uid": "sst1",
    "search_item_type": "tag",
    "search_results_type": "additemoption",
    "button_text": "+ Add Tag",
    "input_name": "newtagname",
    "hidden_input_name": "selectedtagpk",
    "url_endpoint": f"/projects_or_creators_or_tags/0/add-tag/",
    "hx_swap_target": "#my-tags-data",
}

DEFAULT_ADD_CREATOR_SEARCH_SELECT_VARS = {
    "uid": "ssc1",
    "search_item_type": "creator",
    "search_results_type": "additemoption",
    "button_text": "+ Add Creator",
    "input_name": "newcreatorname",
    "hidden_input_name": "selectedcreatorpk",
    "url_endpoint": f"/projects_or_creators/0/add-creator/",
    "hx_swap_target": "#my-creators-data",
}

DEFAULT_ADD_PROJECT_SEARCH_SELECT_VARS = {
    "uid": "ssp1",
    "search_item_type": "project",
    "search_results_type": "additemoption",
    "button_text": "+ Add Project",
    "input_name": "newprojectname",
    "hidden_input_name": "selectedprojectpk",
    "url_endpoint": f"/projects_or_creators/0/add-project/",
    "hx_swap_target": "#my-projects-data",
}


def search_results(request):
    #print(request.headers)
    #print(request.GET)
    #print(request.POST)
    search_term = request.GET.get('search')
    item_type = request.GET.get('searchtype')
    results_type = request.GET.get("resultstype")
    list_id = request.headers.get('Hx-Target')
    context = {"list_id": list_id, "item_type": item_type, "results_type": results_type}
    # don't show the create option for top navbar...NOT a very flexible way of doing things currently
    # also, don't show the option if there's no name for the new item
    if list_id != "search-results-list-0" and search_term != "":
        context["last_list_item"] = f"create & add new {item_type}: \"{search_term}\""
    # select the model based on item_type
    matching_items = apps.get_model(f"core.{item_type}").objects.all()
    if item_type == "tag" or item_type == "creator" or item_type == "project":
        matching_items = matching_items.filter(shareddata__dataname__name__icontains=search_term).distinct()
        # indicate that results should be links to pages
        context["go_to_page"] = True
    elif item_type == "projectseries":
        matching_items = matching_items.filter(name__icontains=search_term)
        # get pk from project info page
        url = request.headers.get("Hx-Current-Url")
        projects_url_index = url.find("/projects/")
        if projects_url_index != -1:
            context["project_id"] = url[projects_url_index+10:len(url)-1]
    if results_type == "additemoption":
        # for showing/hiding elements when a result is selected
        dash_uid_index = list_id.rfind("-")
        if dash_uid_index != -1:
            context["elt_to_show_id"] = "add-new-item-input-wrapper" + list_id[dash_uid_index:]
            context["elt_to_hide_id"] = "add-item-search-select" + list_id[dash_uid_index:]
            context["uid"] = list_id[dash_uid_index+1:]
            context["new_item_name"] = search_term
    # only return the top results (when using fuzzy search, will this still work?)
    context["matching_items"] = matching_items[:5]
    return render(
        request,
        "core/reusable/swaps/search-results-data.html",
        context,
        # required: item_type, results_type, list_id, matching_items
        # extras: last_list_item, go_to_page, (req if projectseries) project_id
    )


def profile_info_edit_sdtype(request, shareddata_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        sdata = SharedData.objects.get(pk=shareddata_id)
        if request.POST.get("pcheck") == "on":
            project, project_created = Project.objects.get_or_create(shareddata=sdata)
        else:
            try:
                project = Project.objects.get(pk=shareddata_id)
                project.delete()
            except Project.DoesNotExist:
                pass
        if request.POST.get("ccheck") == "on":
            creator, creator_created = Creator.objects.get_or_create(shareddata=sdata)
        else:
            try:
                creator = Creator.objects.get(pk=shareddata_id)
                creator.delete()
            except Creator.DoesNotExist:
                pass
        if request.POST.get("tcheck") == "on":
            tag, tag_created = Tag.objects.get_or_create(shareddata=sdata)
        else:
            try:
                tag = Tag.objects.get(pk=shareddata_id)
                tag.delete()
            except Tag.DoesNotExist:
                pass
        # for related pages oob swap
        page_type = None
        if "/projects/" in request.headers.get("Hx-Current-Url"):
            page_type = "project"
        elif "/creators/" in request.headers.get("Hx-Current-Url"):
            page_type = "creator"
        elif "/tags/" in request.headers.get("Hx-Current-Url"):
            page_type = "tag"
        sdtype_data_vars = {"sdata": sdata, "page_type": page_type, "page_updated": True}
        return render(
            request,
            "core/reusable/swaps/profile-shareddata-types-data.html",
            {
                "sdtype_data_vars": sdtype_data_vars,
            }
        )
    return HttpResponse(status=400)


def get_cleaned_search_params(request):
    params = {}
    if request.method == "POST":
        params['search'] = request.POST.get('search')
        params['sortby'] = request.POST.get('sortby')
        params['page'] = request.POST.get('page')
    elif request.method == "GET":
        params['search'] = request.GET.get('search')
        params['sortby'] = request.GET.get('sortby')
        params['page'] = request.GET.get('page')
    # clean all parameters
    if params['search'] == None:
        params['search'] = ""
    if params['sortby'] == None:
        params['sortby'] = ""
    # invalid page numbers are set to page 1
    try:
        params['page'] = int(params['page'])
        if params['page'] < 1:
            params['page'] = 1
    except:
        params['page'] = 1
    return params

def get_library_search_page_navbar(current_page, num_tags, num_tags_per_page):
    relative_pages = {"current_page": current_page, "next_page": current_page+1, "prev_page": current_page-1}
    # page 1 will always exist, even if it is empty
    navbar_pages = [1]
    # calculate the number value of the last page
    last_page_num = math.ceil(num_tags / num_tags_per_page)
    # if you exceed the last page, get set to the last page
    if current_page > last_page_num:
        current_page = last_page_num
    # select 2 numbers before, and 2 numbers after the current page
    close_numbers = range(current_page-2, min(current_page+2+1, last_page_num+1))
    for k in close_numbers:
        if k > 1:
            # add "..." if there is a gap bewteen this and the previous number
            if (navbar_pages[-1] + 1) != k:
                navbar_pages.append("...")
            navbar_pages.append(k)
    # only add the last page if it wasn't already added
    if navbar_pages[-1] < last_page_num:
        # add "..." if there is a gap bewteen this and the previous number
        if (navbar_pages[-1] + 1) != last_page_num:
            navbar_pages.append("...")
        navbar_pages.append(last_page_num)
    return relative_pages, navbar_pages

def get_library_table_data(item_type, search_params, num_tags_per_page):
    # initial set of items will be reduced later on
    if item_type == "tag":
        all_matching_items = Tag.objects.all().select_related("shareddata")
    elif item_type == "creator":
        all_matching_items = Creator.objects.all().select_related("shareddata")
    elif item_type == "project":
        all_matching_items = Project.objects.all().select_related(
            "shareddata"
        ).prefetch_related("creators__shareddata", "tags__shareddata")
    # run the items set through any search parameters that were sent
    all_matching_items = all_matching_items.filter(
        shareddata__dataname__name__icontains=search_params['search']
    ).distinct()
    # sort the results
    if search_params['sortby'] == "date":
        # SWAP THIS OUT FOR ACTUAL DATE when it gets added to the model...
        all_matching_items = all_matching_items.order_by("pk")
    else:
        all_matching_items = all_matching_items.order_by(Lower("shareddata__main_name")) #Lower may not be needed in postgres
    # limit page to have X number of results
    start_index = (search_params['page'] - 1) * num_tags_per_page
    end_index = start_index + num_tags_per_page
    matching_items_1_page = all_matching_items[start_index:end_index]
    # for the resulting set of items, determine if a tag is the first to start with a new letter/character
    # (will be used to display the results like a page in a dictionary)
    prev_first_letter = None
    for item in matching_items_1_page:
        #print(f"get table data loop: {len(connection.queries)}") #TEST
        item.is_first = False
        first_letter = unicodedata.normalize( "NFKD", item.shareddata.main_name )[0].capitalize()
        if first_letter != prev_first_letter:
            item.is_first = True
            prev_first_letter = first_letter
    # return the final results
    return matching_items_1_page, all_matching_items.count() #len(all_matching_items)
###############################################################################
###############################################################################


###############################################################################
# Tag Pages
###############################################################################
TAG_LIBRARY_NUM_ITEMS_PER_PAGE = 50
DEFAULT_ADD_TAG_BUTTON_VARS = {
    "uid": "1",
    "elt_to_show_id": "add-new-item-input-wrapper-1", #make sure correct uid is appended
    "button_text": "+ Add New Tag",
    "input_placeholder": "new tag name",
    "input_name": "newtagname",
    "url_endpoint": "/tags/add-tag/",
    "hx_swap_target": "#library-table-data"
}


def tag_library(request):
    num_tags_per_page = TAG_LIBRARY_NUM_ITEMS_PER_PAGE
    # clean search parameters from GET request
    params = get_cleaned_search_params(request)
    matching_tags, num_tags = get_library_table_data("tag", params, num_tags_per_page)
    relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_tags, num_tags_per_page)
    # params for add-new-item-ui.html
    add_button_vars_1 = DEFAULT_ADD_TAG_BUTTON_VARS.copy()
    # default full page load
    html_page_string = "core/tag-pages/tag-library.html"
    update_library_table_navbar = False
    # partial page load when sorting/filtering/navigating the library
    if request.headers.get('HX-Request') == 'true':
        if request.headers.get('HX-Target') == 'library-table-data':
            html_page_string = "core/tag-pages/swaps/tag-library-table-data.html"
            update_library_table_navbar = True
    return render(
        request, 
        html_page_string, 
        {
            "matching_tags": matching_tags,
            "search_page_numbers": search_page_numbers,
            "relative_page_numbers": relative_page_numbers,
            "params": params,
            "add_button_vars_1": add_button_vars_1,
            "update_library_table_navbar": update_library_table_navbar,
            "test_db_hits": update_library_table_navbar,
            "connection": connection,
        }
    )

def tag_library_add_tag(request):
    if request.method == "POST":
        new_item_name = request.POST.get("newtagname")
        form = AddNewSharedDataForm({"main_name": new_item_name})
        if form.is_valid():
            # create SharedData
            new_sdata = form.save()
            # create Tag linked to SharedData
            new_tag = Tag(shareddata=new_sdata)
            new_tag.save()
            # update the search results
            num_tags_per_page = TAG_LIBRARY_NUM_ITEMS_PER_PAGE
            update_library_table_navbar = True
            # clean search parameters from POST request
            params = get_cleaned_search_params(request)
            matching_tags, num_tags = get_library_table_data("tag", params, num_tags_per_page)
            relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_tags, num_tags_per_page)
            return render(
                request, 
                "core/tag-pages/swaps/tag-library-table-data.html", 
                {
                    "matching_tags": matching_tags,
                    "search_page_numbers": search_page_numbers,
                    "relative_page_numbers": relative_page_numbers,
                    "params": params,
                    "update_library_table_navbar": update_library_table_navbar,
                    "test_db_hits": True,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)


def tag_info(request, tag_id):
    tag = Tag.objects.select_related(
        "shareddata__linked_tag", "shareddata__linked_creator", "shareddata__linked_project"
    ).prefetch_related(
        "related_search_tags__shareddata", "shareddata__dataname_set"
    ).get(pk=tag_id)
    # altnames
    altnames_add_altname_btn_vars = DEFAULT_ADD_ALTNAME_BUTTON_VARS.copy()
    altnames_add_altname_btn_vars["url_endpoint"] = f"/tags/{tag_id}/add-altname/"
    altnames_anlist_vars = {"altnames_list": list(tag.shareddata.dataname_set.all())}
    # profile shareddata type (marked as)
    profile_sdtype_ui_vars = DEFAULT_EDIT_SHAREDDATA_TYPE_UI_VARS.copy()
    profile_sdtype_ui_vars["url_endpoint"] = f"/{tag_id}/edit-sdtype/"
    profile_sdtype_ui_vars["hx_swap_target"] = "#shareddata-type-data"
    profile_sdtype_data_vars = {"sdata": tag.shareddata}
    return render(
        request, 
        "core/tag-pages/tag-info.html", 
        {
            "tag": tag,
            "altnames_add_altname_btn_vars": altnames_add_altname_btn_vars,
            "altnames_anlist_vars": altnames_anlist_vars,
            "profile_sdtype_ui_vars": profile_sdtype_ui_vars,
            "profile_sdtype_data_vars": profile_sdtype_data_vars,
            "connection": connection,
        }
    )

def tag_info_add_altname(request, tag_id):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':
        tag = get_object_or_404(Tag, pk=tag_id)
        new_altname = request.POST.get('newaltname')
        form = AddNewDataNameForm({"name": new_altname, "shareddata": tag.shareddata})
        if form.is_valid():
            form.save()
            # for altname list variables
            trigger_elt_id = request.headers.get("Hx-Trigger")
            anlist_vars = {
                "altnames_list": list(tag.shareddata.dataname_set.all()),
                "altname_added": True,
                "added_altname": new_altname,
                "trigger_uid": trigger_elt_id[trigger_elt_id.rfind("-")+1:]
            }
            return render(
                request, 
                "core/reusable/swaps/alternative-names-data.html", 
                {
                    "anlist_vars": anlist_vars,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)
###############################################################################
###############################################################################


###############################################################################
# Creator Pages
###############################################################################
CREATOR_LIBRARY_NUM_ITEMS_PER_PAGE = 25
DEFAULT_ADD_CREATOR_BUTTON_VARS = {
    "uid": "1",
    "elt_to_show_id": "add-new-item-input-wrapper-1", #make sure correct uid is appended
    "button_text": "+ Add New Creator",
    "input_placeholder": "new creator name",
    "input_name": "newcreatorname",
    "url_endpoint": "/creators/add-creator/",
    "hx_swap_target": "#library-table-data"
}


def creator_library(request):
    num_creators_per_page = CREATOR_LIBRARY_NUM_ITEMS_PER_PAGE
    # clean search parameters from GET request
    params = get_cleaned_search_params(request)
    matching_creators, num_tags = get_library_table_data("creator", params, num_creators_per_page)
    relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_tags, num_creators_per_page)
    # params for add-new-item-ui.html
    add_button_vars_1 = DEFAULT_ADD_CREATOR_BUTTON_VARS.copy()
    # default full page load
    html_page_string = "core/creator-pages/creator-library.html"
    update_library_table_navbar = False
    # partial page load when sorting/filtering/navigating the library
    if request.headers.get('HX-Request') == 'true':
        if request.headers.get('HX-Target') == 'library-table-data':
            html_page_string = "core/creator-pages/swaps/creator-library-table-data.html"
            update_library_table_navbar = True
    return render(
        request, 
        html_page_string, 
        {
            "matching_creators": matching_creators,
            "search_page_numbers": search_page_numbers,
            "relative_page_numbers": relative_page_numbers,
            "params": params,
            "add_button_vars_1": add_button_vars_1,
            "update_library_table_navbar": update_library_table_navbar,
            "test_db_hits": update_library_table_navbar,
            "connection": connection,
        }
    )

def creator_library_add_creator(request):
    if request.method == "POST":
        new_item_name = request.POST.get("newcreatorname")
        form = AddNewSharedDataForm({"main_name": new_item_name})
        if form.is_valid():
            # create SharedData
            new_sdata = form.save()
            # create Creator linked to SharedData
            new_creator = Creator(shareddata=new_sdata)
            new_creator.save()
            # update the search results
            num_creators_per_page = CREATOR_LIBRARY_NUM_ITEMS_PER_PAGE
            update_library_table_navbar = True
            # clean search parameters from POST request
            params = get_cleaned_search_params(request)
            matching_creators, num_creators = get_library_table_data("creator", params, num_creators_per_page)
            relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_creators, num_creators_per_page)
            return render(
                request, 
                "core/creator-pages/swaps/creator-library-table-data.html", 
                {
                    "matching_creators": matching_creators,
                    "search_page_numbers": search_page_numbers,
                    "relative_page_numbers": relative_page_numbers,
                    "params": params,
                    "update_library_table_navbar": update_library_table_navbar,
                    "test_db_hits": True,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)


def creator_info(request, creator_id):
    creator = Creator.objects.select_related(
        "shareddata__linked_creator", 
        "shareddata__linked_project", 
        "shareddata__linked_tag"
    ).prefetch_related(
        "shareddata__dataname_set", 
        "circles__shareddata", 
        "circle_members__shareddata", 
        "project_set__shareddata", 
        "content_tags__shareddata"
    ).get(pk=creator_id)
    # altnames
    altnames_add_altname_btn_vars = DEFAULT_ADD_ALTNAME_BUTTON_VARS.copy()
    altnames_add_altname_btn_vars["url_endpoint"] = f"/creators/{creator_id}/add-altname/"
    altnames_anlist_vars = {"altnames_list": list(creator.shareddata.dataname_set.all())}
    # profile shareddata type (marked as)
    profile_sdtype_ui_vars = DEFAULT_EDIT_SHAREDDATA_TYPE_UI_VARS.copy()
    profile_sdtype_ui_vars["url_endpoint"] = f"/{creator_id}/edit-sdtype/"
    profile_sdtype_ui_vars["hx_swap_target"] = "#shareddata-type-data"
    profile_sdtype_data_vars = {"sdata": creator.shareddata}
    # circles
    circles_list_vars = {"list_id": "circles-list", "matching_creators": creator.circles.all()}
    circles_add_creator_ss_vars = DEFAULT_ADD_CREATOR_SEARCH_SELECT_VARS.copy()
    circles_add_creator_ss_vars["url_endpoint"] = f"/creators/{creator_id}/add-creator/"
    circles_add_creator_ss_vars["hx_swap_target"] = f"#circles-list"
    # members
    members_list_vars = {"list_id": "members-list", "matching_creators": creator.circle_members.all()}
    members_add_creator_ss_vars = DEFAULT_ADD_CREATOR_SEARCH_SELECT_VARS.copy()
    members_add_creator_ss_vars["url_endpoint"] = f"/creators/{creator_id}/add-creator/"
    members_add_creator_ss_vars["hx_swap_target"] = f"#members-list"
    members_add_creator_ss_vars["uid"] = "ssc2"
    # content tags
    contenttags_add_tag_ss_vars = DEFAULT_ADD_TAG_SEARCH_SELECT_VARS.copy()
    contenttags_add_tag_ss_vars["url_endpoint"] = f"/creators/{creator_id}/add-tag/"
    contenttags_add_tag_ss_vars["hx_swap_target"] = f"#swappable-tags-list-data"
    contenttags_tlist_vars = {"matching_tags": creator.content_tags.all()}
    return render(
        request,
        "core/creator-pages/creator-info.html",
        {
            "creator": creator,
            "altnames_add_altname_btn_vars": altnames_add_altname_btn_vars,
            "altnames_anlist_vars": altnames_anlist_vars,
            "profile_sdtype_ui_vars": profile_sdtype_ui_vars,
            "profile_sdtype_data_vars": profile_sdtype_data_vars,
            "circles_list_vars": circles_list_vars,
            "circles_add_creator_ss_vars": circles_add_creator_ss_vars,
            "members_list_vars": members_list_vars,
            "members_add_creator_ss_vars": members_add_creator_ss_vars,
            "contenttags_add_tag_ss_vars": contenttags_add_tag_ss_vars,
            "contenttags_tlist_vars": contenttags_tlist_vars,
            "connection": connection,
         }
    )

def creator_info_add_altname(request, creator_id):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':
        creator = get_object_or_404(Creator, pk=creator_id)
        new_altname = request.POST.get('newaltname')
        form = AddNewDataNameForm({"name": new_altname, "shareddata": creator.shareddata})
        if form.is_valid():
            form.save()
            # for altname list variables
            trigger_elt_id = request.headers.get("Hx-Trigger")
            anlist_vars = {
                "altnames_list": list(creator.shareddata.dataname_set.all()),
                "altname_added": True,
                "added_altname": new_altname,
                "trigger_uid": trigger_elt_id[trigger_elt_id.rfind("-")+1:]
            }
            return render(
                request, 
                "core/reusable/swaps/alternative-names-data.html", 
                {
                    "anlist_vars": anlist_vars,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)

def creator_info_add_creator(request, creator_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_creator_name = request.POST.get("newcreatorname")
        selected_creator_pk = request.POST.get("selectedcreatorpk")
        creator = Creator.objects.get(pk=creator_id)
        if new_creator_name != "" and selected_creator_pk == "":
            form = AddNewSharedDataForm({"main_name": new_creator_name})
            if form.is_valid():
                new_sdata = form.save()
                creator_to_add = Creator.objects.create(shareddata=new_sdata)
        elif selected_creator_pk != "" and new_creator_name == "":
            creator_to_add = Creator.objects.get(pk=selected_creator_pk)
        target_elt_id = request.headers.get("Hx-Target")
        clist_vars = {"list_id": target_elt_id}
        # determine whether you're adding a member or a circle, and act accordingly
        if target_elt_id == "circles-list":
            creator.circles.add(creator_to_add)
            clist_vars["matching_creators"] = creator.circles.all()
        elif target_elt_id == "members-list":
            creator_to_add.circles.add(creator)
            clist_vars["matching_creators"] = creator.circle_members.all()
        return render(
            request,
            "core/reusable/swaps/creators-list-data.html",
            {
                "clist_vars": clist_vars,
            }
        )
    return HttpResponse(status=400)

def creator_info_add_tag(request, creator_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_tag_name = request.POST.get("newtagname")
        selected_tag_pk = request.POST.get("selectedtagpk")
        creator = Creator.objects.get(pk=creator_id)
        if new_tag_name != "" and selected_tag_pk == "":
            form = AddNewSharedDataForm({"main_name": new_tag_name})
            if form.is_valid():
                new_sdata = form.save()
                tag = Tag.objects.create(shareddata=new_sdata)
        elif selected_tag_pk != "" and new_tag_name == "":
            tag = Tag.objects.get(pk=selected_tag_pk)
        creator.content_tags.add(tag)
        # content tags data
        tlist_vars = {
            "matching_tags": creator.content_tags.all(),
        }
        return render(
            request,
            "core/reusable/swaps/tags-list-data.html",
            {
                "tlist_vars": tlist_vars,
            }
        )
    return HttpResponse(status=400)
###############################################################################
###############################################################################


###############################################################################
# PROJECT PAGES
###############################################################################
PROJECT_LIBRARY_NUM_ITEMS_PER_PAGE = 10
DEFAULT_ADD_PROJECT_BUTTON_VARS = {
    "uid": "1",
    "elt_to_show_id": "add-new-item-input-wrapper-1", #make sure correct uid is appended
    "button_text": "+ Add New Project",
    "input_placeholder": "new project name",
    "input_name": "newprojectname",
    "url_endpoint": "/projects/add-project/",
    "hx_swap_target": "#library-table-data"
}

DEFAULT_ADD_SERIES_SEARCH_SELECT_VARS = {
    "uid": "sss1",
    "search_item_type": "projectseries",
    "search_results_type": "additemoption",
    "button_text": "+ Add/Edit Series",
    "input_name": "newseriesname",
    "hidden_input_name": "selectedseriespk",
    "url_endpoint": f"/projects/0/add-series/",
    "hx_swap_target": "#prequel-sequel-projects",
}


def project_library(request):
    num_items_per_page = PROJECT_LIBRARY_NUM_ITEMS_PER_PAGE
    # clean search parameters from GET request
    params = get_cleaned_search_params(request)
    matching_items, num_items = get_library_table_data("project", params, num_items_per_page)
    relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_items, num_items_per_page)
    # params for add-new-item-ui.html
    add_button_vars_1 = DEFAULT_ADD_PROJECT_BUTTON_VARS.copy()
    # default full page load
    html_page_string = "core/project-pages/project-library.html"
    update_library_table_navbar = False
    # partial page load when sorting/filtering/navigating the library
    if request.headers.get('HX-Request') == 'true':
        if request.headers.get('HX-Target') == 'library-table-data':
            html_page_string = "core/project-pages/swaps/project-library-table-data.html"
            update_library_table_navbar = True
    return render(
        request, 
        html_page_string, 
        {
            "matching_items": matching_items,
            "search_page_numbers": search_page_numbers,
            "relative_page_numbers": relative_page_numbers,
            "params": params,
            "add_button_vars_1": add_button_vars_1,
            "update_library_table_navbar": update_library_table_navbar,
            "test_db_hits": update_library_table_navbar,
            "connection": connection,
        }
    )

def project_library_add_project(request):
    if request.method == "POST":
        new_item_name = request.POST.get("newprojectname")
        form = AddNewSharedDataForm({"main_name": new_item_name})
        if form.is_valid():
            # create SharedData
            new_sdata = form.save()
            # create Project
            new_project = Project(shareddata=new_sdata)
            new_project.save()
            # create Tag linked to SharedData
            new_tag = Tag(shareddata=new_sdata)
            new_tag.save()
            # update the search results
            num_items_per_page = PROJECT_LIBRARY_NUM_ITEMS_PER_PAGE
            update_library_table_navbar = True
            # clean search parameters from POST request
            params = get_cleaned_search_params(request)
            matching_items, num_items = get_library_table_data("project", params, num_items_per_page)
            relative_page_numbers, search_page_numbers = get_library_search_page_navbar(params['page'], num_items, num_items_per_page)
            return render(
                request, 
                "core/project-pages/swaps/project-library-table-data.html", 
                {
                    "matching_items": matching_items,
                    "search_page_numbers": search_page_numbers,
                    "relative_page_numbers": relative_page_numbers,
                    "update_library_table_navbar": update_library_table_navbar,
                    "test_db_hits": True,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)


def project_info(request, project_id):
    project = Project.objects.select_related(
        "shareddata__linked_tag", "shareddata__linked_project", "shareddata__linked_creator"
    ).prefetch_related(
        "creators__shareddata", "tags__shareddata", "shareddata__dataname_set"
    ).get(pk=project_id)
    # for putting commas in lists
    project_creators = project.creators.all()
    last_creator_index = len(project_creators) - 1
    last_creator = project_creators[last_creator_index] if last_creator_index > -1 else None
    # altnames
    altnames_add_altname_btn_vars = DEFAULT_ADD_ALTNAME_BUTTON_VARS.copy()
    altnames_add_altname_btn_vars["url_endpoint"] = f"/projects/{project_id}/add-altname/"
    altnames_anlist_vars = {"altnames_list": list(project.shareddata.dataname_set.all())}
    # profile info dates
    profile_rdate_edit_date_ui_vars = DEFAULT_EDIT_DATE_UI_VARS.copy()
    profile_rdate_edit_date_ui_vars["url_endpoint"] = f"/projects/{project_id}/edit-date/"
    profile_rdate_edit_date_ui_vars["hx_swap_target"] = "#rdate-data"
    profile_rdate_edit_date_ui_vars["my_tr_id"] = "hidden-rdate-input"
    profile_rdate_edit_date_ui_vars["message_list_id"] = "message-list-rdate"
    profile_ludate_edit_date_ui_vars = DEFAULT_EDIT_DATE_UI_VARS.copy()
    profile_ludate_edit_date_ui_vars["url_endpoint"] = f"/projects/{project_id}/edit-date/"
    profile_ludate_edit_date_ui_vars["hx_swap_target"] = "#ludate-data"
    profile_ludate_edit_date_ui_vars["my_tr_id"] = "hidden-ludate-input"
    profile_ludate_edit_date_ui_vars["message_list_id"] = "message-list-ludate"
    profile_ludate_edit_date_ui_vars["uid"] = "ed2"
    # profile shareddata type (marked as)
    profile_sdtype_ui_vars = DEFAULT_EDIT_SHAREDDATA_TYPE_UI_VARS.copy()
    profile_sdtype_ui_vars["url_endpoint"] = f"/{project_id}/edit-sdtype/"
    profile_sdtype_ui_vars["hx_swap_target"] = "#shareddata-type-data"
    profile_sdtype_data_vars = {"sdata": project.shareddata}
    # tags
    alltags_add_tag_ss_vars = DEFAULT_ADD_TAG_SEARCH_SELECT_VARS.copy()
    alltags_add_tag_ss_vars["url_endpoint"] = f"/projects/{project_id}/add-tag/"
    alltags_add_tag_ss_vars["hx_swap_target"] = "#swappable-tags-list-data"
    alltags_add_tag_ss_vars["search_filter_sort"] = True
    alltags_tlist_vars = {"matching_tags": project.tags.all()[:20]}
    # add series buttons/ui
    preseq_add_series_ss_vars = DEFAULT_ADD_SERIES_SEARCH_SELECT_VARS.copy()
    preseq_add_series_ss_vars["url_endpoint"] = f"/projects/{project_id}/add-series/"
    preseq_add_series_ss_vars["hx_swap_target"] = "#prequel-projects-data"
    # get series data
    preseq_series_data = project.related_series.all()
    for pseries in preseq_series_data:
        pseries.proj_order_num = pseries.get_entry(project)
    prequel_pseries_data_vars = {
        "series_data": preseq_series_data,
        "tab_id": "prequel-projects-data",
    }
    sequel_pseries_data_vars = {
        "series_data": preseq_series_data,
        "tab_id": "sequel-projects-data",
    }
    # other related projects
    other_add_project_ss_vars = DEFAULT_ADD_PROJECT_SEARCH_SELECT_VARS.copy()
    other_add_project_ss_vars["url_endpoint"] = f"/projects/{project_id}/add-project/"
    other_add_project_ss_vars["hx_swap_target"] = f"#other-projects-data"
    other_pdata_vars = {"matching_projects": project.other_related_projects.all()}
    # Created By section
    createdby_add_creator_ss_vars = DEFAULT_ADD_CREATOR_SEARCH_SELECT_VARS.copy()
    createdby_add_creator_ss_vars["url_endpoint"] = f"/projects/{project_id}/add-creator/"
    createdby_add_creator_ss_vars["hx_swap_target"] = "#all-creators-data"
    createdby_clist_vars = {"matching_creators": project.creators.all()}
    # featured in works by
    featuredin_add_creator_ss_vars = DEFAULT_ADD_CREATOR_SEARCH_SELECT_VARS.copy()
    featuredin_add_creator_ss_vars["uid"] = "ssc2"
    featuredin_add_creator_ss_vars["url_endpoint"] = f"/projects/{project_id}/add-content-creator/"
    featuredin_add_creator_ss_vars["hx_swap_target"] = "#content-creators-data"
    return render(
        request, 
        "core/project-pages/project-info.html", 
        {
            "project": project,
            "altnames_anlist_vars": altnames_anlist_vars,
            "altnames_add_altname_btn_vars": altnames_add_altname_btn_vars,
            "profile_rdate_edit_date_ui_vars": profile_rdate_edit_date_ui_vars,
            "profile_ludate_edit_date_ui_vars": profile_ludate_edit_date_ui_vars,
            "profile_sdtype_ui_vars": profile_sdtype_ui_vars,
            "profile_sdtype_data_vars": profile_sdtype_data_vars,
            "alltags_add_tag_ss_vars": alltags_add_tag_ss_vars,
            "alltags_tlist_vars": alltags_tlist_vars,
            "include_add_tag_button": True,
            "createdby_add_creator_ss_vars": createdby_add_creator_ss_vars,
            "createdby_clist_vars": createdby_clist_vars,
            "preseq_add_series_ss_vars": preseq_add_series_ss_vars,
            "prequel_pseries_data_vars": prequel_pseries_data_vars,
            "sequel_pseries_data_vars": sequel_pseries_data_vars,
            "other_add_project_ss_vars": other_add_project_ss_vars,
            "other_pdata_vars": other_pdata_vars,
            "featuredin_add_creator_ss_vars": featuredin_add_creator_ss_vars,
            "last_creator": last_creator,
            "connection": connection,
        }
    )

def project_info_add_altname(request, project_id):
    if request.method == "POST" and request.headers.get('Hx-Request') == 'true':
        project = get_object_or_404(Project, pk=project_id)
        new_altname = request.POST.get('newaltname')
        form = AddNewDataNameForm({"name": new_altname, "shareddata": project.shareddata})
        if form.is_valid():
            form.save()
            # for altname list variables
            trigger_elt_id = request.headers.get("Hx-Trigger")
            anlist_vars = {
                "altnames_list": list(project.shareddata.dataname_set.all()),
                "altname_added": True,
                "added_altname": new_altname,
                "trigger_uid": trigger_elt_id[trigger_elt_id.rfind("-")+1:]
            }
            return render(
                request, 
                "core/reusable/swaps/alternative-names-data.html", 
                {
                    "anlist_vars": anlist_vars,
                    "connection": connection,
                }
            )
    return HttpResponse(status=400)

def project_info_vote_overall_score(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_score = request.POST.get("newscorevalue")
        form = SubmitProjectOverallScoreBallotForm({"score": new_score})
        if form.is_valid():
            time_now = timezone.now()
            # obfuscate user's identity
            if settings.DATABASES["default"]["HOST"] == "localhost":
                binary_ip = request.META.get("REMOTE_ADDR").encode()
                pepper = b"test"
            else:
                binary_ip = request.META.get("HTTP_X_FORWARDED_FOR").encode()
                pepper_file = open(f"/ppprs/{time_now.year}_{time_now.month}", "rb")
                pepper = pepper_file.read()
                pepper_file.close()
            new_hash = hashlib.pbkdf2_hmac("sha256", binary_ip, pepper, 1)
            new_salt = os.urandom(16)
            # add/update score to database
            project = Project.objects.get(pk=project_id)
            ballot, created = OverallProjectScoreBallot.objects.get_or_create(project=project, uid_hash=new_hash)
            if created:
                ballot.uid_salt = new_salt
            ballot.score = form.cleaned_data["score"]
            ballot.submitted_on = time_now
            ballot.save()
            # scores probably won't update instantly in future, so this part can probably be deleted later
            all_overall_score_ballots = OverallProjectScoreBallot.objects.filter(project=project)
            average_score = all_overall_score_ballots.aggregate(Avg("score"))
            project.overall_score = average_score["score__avg"]
            project.save()
            #might need this for success message? (trigger_uid and other stuff)
            #oscore_data_vars = {"project": project}
            return render(
                request,
                "core/project-pages/swaps/project-info-overall-score-data.html",
                {
                    "project": project,
                    #"oscore_data_vars": oscore_data_vars
                }
        )
    return HttpResponse(status=400)

def project_info_edit_date(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        trigger_elt_id = request.headers.get("Hx-Trigger")
        target_elt = request.headers.get("Hx-Target")
        new_date_value = request.POST.get("newdatevalue")
        # release date & last update date are the same type of data; so i chose this one to check against
        form = EditProjectDateForm({"release_date": new_date_value})
        if form.is_valid():
            project = Project.objects.get(pk=project_id)
            eddata_vars = {}
            if target_elt == "rdate-data":
                project.release_date = form.cleaned_data["release_date"]
                project.save()
                eddata_vars["rdate_updated"] = True
            elif target_elt == "ludate-data":
                project.last_update_date = form.cleaned_data["release_date"]
                project.save()
                eddata_vars["ludate_updated"] = True
            return render(
                request,
                "core/project-pages/swaps/project-info-profile-date-data.html",
                {
                    "project": project,
                    "eddata_vars": eddata_vars,
                }
            )
    return HttpResponse(status=400)

def project_info_add_tag(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
            new_tag_name = request.POST.get("newtagname")
            selected_tag_pk = request.POST.get("selectedtagpk")
            project = Project.objects.get(pk=project_id)
            if new_tag_name == "" and selected_tag_pk != "":
                tag = Tag.objects.get(pk=selected_tag_pk)
            elif new_tag_name != "" and selected_tag_pk == "":
                form = AddNewSharedDataForm({"main_name": new_tag_name})
                if form.is_valid():
                    new_sdata = form.save()
                    tag = Tag.objects.create(shareddata=new_sdata)
            project.tags.add(tag)
            # display tags depending on current search options
            search_term = request.POST.get("currsearch") if request.POST.get("currsearch") != None else ""
            sort_by = request.POST.get("currsort") if request.POST.get("currsort") != None else ""
            matching_items = project.tags.all()
            if search_term != "":
                matching_items = matching_items.filter(shareddata__dataname__name__icontains=search_term).distinct()
            if sort_by == "rating":
                pass
            elif sort_by == "relevance":
                pass
            else: #sort by name
                matching_items = matching_items.order_by(Lower("shareddata__main_name"))
            # data for template
            tlist_vars = {
                "matching_tags": matching_items[:20],
            }
            return render(
                request, 
                "core/reusable/swaps/tags-list-data.html",
                {
                    "tlist_vars": tlist_vars,
                }
            )
    return HttpResponse(status=400)

def project_info_search_tags(request, project_id):
    if request.headers.get("Hx-Request") == "true":
        # clean search params
        search_term = request.GET.get("search") if request.GET.get("search") != None else ""
        sort_by = request.GET.get("sortby") if request.GET.get("sortby") != None else ""
        # filter/sort the tag results
        matching_items = Project.objects.get(pk=project_id).tags.all()
        if search_term != "":
            matching_items = matching_items.filter(shareddata__dataname__name__icontains=search_term).distinct()
        # sorting (currently not functional without voting implemented)
        if sort_by == "rating":
            pass
        elif sort_by == "relevance":
            pass
        else: #sort by name
            matching_items = matching_items.order_by(Lower("shareddata__main_name")) #lower not needed in postgres?
        tlist_vars = {"matching_tags": matching_items[:20]}
        return render(
            request,
            "core/reusable/swaps/tags-list-data.html",
            {
                "tlist_vars": tlist_vars,
            }
        )
    return HttpResponse(status=400)

def project_info_add_series(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_series_name = request.POST.get(f"newseriesname")
        selected_series_pk = request.POST.get(f"selectedseriespk")
        project = Project.objects.get(pk=project_id)
        if new_series_name != "" and selected_series_pk == "":
            form = AddNewProjectSeriesForm({"name": new_series_name})
            if form.is_valid():
                # make a new series and add the project to it
                series = form.save()
                ProjectSeriesEntry.objects.create(projectseries=series, project=project)
        elif selected_series_pk != "" and new_series_name == "":
            series = ProjectSeries.objects.get(pk=selected_series_pk)
            adjacent_entry = request.POST.get("adjacententry")
            relative_position = request.POST.get("relativeposition")
            if request.POST.get("adjacententry") != "":
                adjacent_entry = ProjectSeriesEntry.objects.get(pk=adjacent_entry)
            # add the project to the series
            new_entry, created = ProjectSeriesEntry.objects.get_or_create(
                projectseries=series, project=project
            )
            new_entry.save(adj_entry=adjacent_entry, rel_pos=relative_position)
        # get series data
        series_data = project.related_series.all()
        for pseries in series_data:
            pseries.proj_order_num = pseries.get_entry(project)
        # tab_id, opp_tab_id
        tab_id = request.headers.get("Hx-Target")
        if tab_id == "prequel-projects-data":
            opp_tab_id = "sequel-projects-data"
        elif tab_id == "sequel-projects-data":
            opp_tab_id = "prequel-projects-data"
        # series data vars
        pseries_data_vars = {
            "series_data": series_data,
            "tab_id": tab_id,
            "series_updated": True,
        }
        opposite_pseries_data_vars = {
            "series_data": series_data,
            "tab_id": opp_tab_id,
        }
        return render(
            request,
            "core/project-pages/swaps/project-info-series-data.html",
            {
                "project": project,
                "pseries_data_vars": pseries_data_vars,
                "opposite_pseries_data_vars": opposite_pseries_data_vars,
                "connection": connection,
            }
        )
    return HttpResponse(status=400)

def project_info_preview_pseries(request, project_id, pseries_id):
    if request.headers.get("Hx-Request") == "true":
        # get uid
        target_elt_id = request.headers.get("Hx-Target")
        dash_uid_index = target_elt_id.rfind('-')
        uid = target_elt_id[dash_uid_index+1:]
        # get other data
        project = Project.objects.get(pk=project_id)
        projectseries = ProjectSeries.objects.get(pk=pseries_id)
        series_entries = ProjectSeriesEntry.objects.filter(projectseries=pseries_id).order_by("order_num")
        return render(
            request, 
            "core/reusable/swaps/preview-project-series-data.html", 
            {
                "project": project,
                "uid": uid,
                "projectseries": projectseries,
                "series_entries": series_entries,
            }
        )
    return HttpResponse(status=400)

def project_info_add_project(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_project_name = request.POST.get("newprojectname")
        selected_project_pk = request.POST.get("selectedprojectpk")
        if new_project_name != "" and selected_project_pk == "":
            form = AddNewSharedDataForm({"main_name": new_project_name})
            if form.is_valid():
                sdata = form.save()
                project_to_add = Project.objects.create(shareddata=sdata)
        elif selected_project_pk != "" and new_project_name == "":
            project_to_add = Project.objects.get(pk=selected_project_pk)
        project = Project.objects.get(pk=project_id)
        project.other_related_projects.add(project_to_add)
        # pdata_vars
        other_pdata_vars = {
            "matching_projects": project.other_related_projects.all(),
        }
        return render(
            request,
            "core/project-pages/swaps/project-info-other-related-projects-data.html",
            {
                "pdata_vars": other_pdata_vars,
            }
        )
    return HttpResponse(status=400)

def project_info_add_creator(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_creator_name = request.POST.get("newcreatorname")
        selected_creator_pk = request.POST.get("selectedcreatorpk")
        project = Project.objects.get(pk=project_id)
        if new_creator_name != "" and selected_creator_pk == "":
            form = AddNewSharedDataForm({"main_name": new_creator_name})
            if form.is_valid():
                new_sdata = form.save()
                creator = Creator.objects.create(shareddata=new_sdata)
        elif selected_creator_pk != "" and new_creator_name == "":
            creator = Creator.objects.get(pk=selected_creator_pk)
        project.creators.add(creator)
        # clist_vars
        matching_creators = project.creators.all()
        last_creator_index = len(matching_creators) - 1
        last_creator = matching_creators[last_creator_index] if last_creator_index > -1 else None
        createdby_clist_vars = {
            "update_project_info_main_creators": True,
            "matching_creators": matching_creators,
            "last_creator": last_creator,
        }
        return render(
            request,
            "core/reusable/swaps/creators-list-data.html",
            {
                "clist_vars": createdby_clist_vars,
            }
        )
    return HttpResponse(status=400)

def project_info_add_content_creator(request, project_id):
    if request.method == "POST" and request.headers.get("Hx-Request") == "true":
        new_creator_name = request.POST.get("newcreatorname")
        selected_creator_pk = request.POST.get("selectedcreatorpk")
        project = Project.objects.select_related("shareddata__linked_tag").get(pk=project_id)
        profile_info_update_required = False
        sdtype_data_vars = {}
        # get or create creator
        if new_creator_name != "" and selected_creator_pk == "":
            form = AddNewSharedDataForm({"main_name": new_creator_name})
            if form.is_valid():
                new_sdata = form.save()
                creator = Creator.objects.create(shareddata=new_sdata)
        elif selected_creator_pk != "" and new_creator_name == "":
            creator = Creator.objects.get(pk=selected_creator_pk)
        # add this project to content tags
        # DO YOU REALLY want to create the linked tag if the project isn't marked as Tag?
        # THINK ABOUT if you're doing too much, or if restricting it is better, or if it's fine
        if not Tag.objects.filter(pk=project_id).exists():
            Tag.objects.create(shareddata=project.shareddata)
            profile_info_update_required = True
            sdtype_data_vars = {
                "page_updated": True,
                "sdata": project.shareddata,
                "page_type": "project",
                "sdtdata_is_oob": True,
            }
        creator.content_tags.add(project.shareddata.linked_tag)
        return render(
            request,
            "core/project-pages/swaps/project-info-content-creators-data.html",
            {
                "project": project,
                "profile_info_update_required": profile_info_update_required,
                "sdtype_data_vars": sdtype_data_vars,
            }
        )
    return HttpResponse(status=400)
###############################################################################
###############################################################################


###############################################################################
# EDIT REQUESTS
###############################################################################
def editreq_index(request):
    latest_editreq_list = EditRequest.objects.order_by("-created_date")[:10]
    context = {
        "latest_editreq_list": latest_editreq_list,
    }
    return render(request, "core/edit-requests/index.html", context)


def editreq_detail(request, editreq_id):
    editreq = get_object_or_404(EditRequest, pk=editreq_id)
    return render(request, "core/edit-requests/detail.html", {"editreq": editreq})


def editreq_results(request, editreq_id):
    editreq = get_object_or_404(EditRequest, pk=editreq_id)
    return render(request, "core/edit-requests/results.html", {"editreq": editreq})


def editreq_vote(request, editreq_id):
    editreq = get_object_or_404(EditRequest, pk=editreq_id)
    related_comments = editreq.editrequestcomment_set.all()

    selected_choices_array = []
    for comment in related_comments:
        try:
            myname = "pro_con" + str(comment.id)
            selected_choice = editreq.editrequestcomment_set.get(pk=comment.id)
            selected_choice_value = request.POST[myname]
        except (KeyError, EditRequestComment.DoesNotExist):
            bad_choice_text = "(" + str(comment.id) + ")" + comment.pro_con_text
            return render(
                request,
                "core/edit-requests/detail.html",
                {
                    "editreq": editreq,
                    "error_message": "You didn't select a choice for " + bad_choice_text
                }
            )
        else:
            selected_choices_array.append((selected_choice, selected_choice_value))

    # this should only run if no errors            
    for schoice_tuple in selected_choices_array:
        if schoice_tuple[1] == "agree":
            schoice_tuple[0].upvotes += 1
        elif schoice_tuple[1] == "disagree":
            schoice_tuple[0].upvotes -= 1
        schoice_tuple[0].save()
    
    return HttpResponseRedirect(reverse("core:er_results", args=(editreq.id,)))
###############################################################################
###############################################################################