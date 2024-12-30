from django.forms import ModelForm

from .models import SharedData, DataName, ProjectSeries, Project, OverallProjectScoreBallot


#########################################################################
# Generic Data for Tag, Creator, Project
#########################################################################
class AddNewSharedDataForm(ModelForm):
    class Meta:
        model = SharedData
        fields = ["main_name"]

class AddNewDataNameForm(ModelForm):
    class Meta:
        model = DataName
        fields = ["name", "shareddata"]
#########################################################################
#########################################################################


#########################################################################
# Tags
#########################################################################
#########################################################################
#########################################################################


#########################################################################
# Creators
#########################################################################
#########################################################################
#########################################################################


#########################################################################
# Projects
#########################################################################
class AddNewProjectSeriesForm(ModelForm):
    class Meta:
        model = ProjectSeries
        fields = ["name"]

# planning on using this to update both release date and last update date
class EditProjectDateForm(ModelForm):
    class Meta:
        model = Project
        fields = ["release_date"]

class SubmitProjectOverallScoreBallotForm(ModelForm):
    class Meta:
        model = OverallProjectScoreBallot
        fields = ["score"]
#########################################################################
#########################################################################