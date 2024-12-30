from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.index, name="index"),
    #ex: /edit-requests/
    path("edit-requests/", views.editreq_index, name="er_index"),
    # ex: /edit-requests/5/
    path("edit-requests/<int:editreq_id>/", views.editreq_detail, name="er_detail"),
    # ex: /edit-requests/5/results/
    path("edit-requests/<int:editreq_id>/results/", views.editreq_results, name="er_results"),
    # ex: /edit-requests/5/vote/
    path("edit-requests/<int:editreq_id>/vote/", views.editreq_vote, name="er_vote"),

    # ex: /under-construction/
    path("under-construction/", views.under_construction, name="under_construction"),    

    # ex: /search-results/
    # ex: /search-results/?search=term
    path("search-results/", views.search_results, name="search_results"),
    # ex: /123456789/edit-sdtype/
    path("<int:shareddata_id>/edit-sdtype/", views.profile_info_edit_sdtype, name="profile_info_edit_sdtype"),
    # ex: /tags/
    # ex: /tags/?search=term&sortby=date&page=5
    path("tags/", views.tag_library, name="tag_library"),
    # ex: /tags/add-tag/
    path("tags/add-tag/", views.tag_library_add_tag),
    # ex: /tags/123456789/
    path("tags/<int:tag_id>/", views.tag_info, name="tag_info"),
    # ex: /tags/123456789/add-altname/
    path("tags/<int:tag_id>/add-altname/", views.tag_info_add_altname),
    # ex: /projects/
    path("projects/", views.project_library, name="project_library"),
    # ex: /projects/add-project/
    path("projects/add-project/", views.project_library_add_project, name="project_library_add_project"),
    # ex: /projects/123456789/
    path("projects/<int:project_id>/", views.project_info, name="project_info"),
    # ex: /projects/123456789/add-altname/
    path("projects/<int:project_id>/add-altname/", views.project_info_add_altname, name="project_info_add_altname"),
    # ex: /projects/123456789/vote-overall-score/
    path("projects/<int:project_id>/vote-overall-score/", views.project_info_vote_overall_score, name="project_info_vote_overall_score"),
    # ex: /projects/123456789/edit-date/
    path("projects/<int:project_id>/edit-date/", views.project_info_edit_date, name="project_info_edit_date"),
    # ex: /projects/123456789/add-tag/
    path("projects/<int:project_id>/add-tag/", views.project_info_add_tag, name="project_info_add_tag"),
    # ex: /projects/123456789/search-tag/
    path("projects/<int:project_id>/search-tags/", views.project_info_search_tags, name="project_info_search_tags"),
    # ex: /projects/123456789/add-series/
    path("projects/<int:project_id>/add-series/", views.project_info_add_series, name="project_info_add_series"),
    # ex: /projects/123456789/preview-series/987654321
    path("projects/<int:project_id>/preview-pseries/<int:pseries_id>/", views.project_info_preview_pseries, name="project_info_preview_pseries"),
    # ex: /projects/123456789/add-project/
    path("projects/<int:project_id>/add-project/", views.project_info_add_project, name="project_info_add_project"),
    # ex: /projects/123456789/add-creator/
    path("projects/<int:project_id>/add-creator/", views.project_info_add_creator, name="project_info_add_creator"),
    # ex: /projects/123456789/add-content-creator/
    path("projects/<int:project_id>/add-content-creator/", views.project_info_add_content_creator, name="project_info_add_content_creator"),
    # ex: /creators/
    # ex: /creators/?search=term&sortby=date&page=5
    path("creators/", views.creator_library, name="creator_library"),
    # ex: /creators/add-creator/
    path("creators/add-creator/", views.creator_library_add_creator),
    # ex: /creators/123456789/
    path("creators/<int:creator_id>/", views.creator_info, name="creator_info"),
    # ex: /creators/123456789/add-altname/
    path("creators/<int:creator_id>/add-altname/", views.creator_info_add_altname),
    # ex: /creators/123456789/add-creator/
    path("creators/<int:creator_id>/add-creator/", views.creator_info_add_creator, name="creator_info_add_creator"),
    # ex: /creators/123456789/add-tag/
    path("creators/<int:creator_id>/add-tag/", views.creator_info_add_tag, name="creator_info_add_tag"),
    # ex: /maintenance/approved-tag-types/

    ####################################################################################################
    ## TEST PAGES USED FOR TESTING
    ####################################################################################################
    # ex: /test/
    path("test/", views.test_main, name="test_main"),
    # ex: /test/123456789/next/
    path("test/partial/", views.test_partial, name="test_partial"),
    # ex: /test/post-success/
    path("test/post-success", views.test_post, name="test_post_success"),
]