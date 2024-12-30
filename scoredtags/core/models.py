import datetime

from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

#################################################################################
# Pages and Tags
#################################################################################
# abstract parent which can have one of each: Tag, Creator, Project
class SharedData(models.Model):
    main_name = models.CharField(max_length=50)

    def __str__(self):
        return self.main_name
    
    def save(self, *args, **kwargs):
        being_created = (self.pk == None)
        super().save(*args, **kwargs)
        # add a new DataName for a newly created SharedData
        if being_created:
            new_name = DataName(name=self.main_name, shareddata=self)
            new_name.save()


# will be used when searching for alternative names/aliases of projects/tags/creators
class DataName(models.Model):
    name = models.CharField(max_length=200)
    shareddata = models.ForeignKey(SharedData, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# for storing all approved tag types (i.e. contents tags, genre tags, media/service type tags, etc.)
class TagType(models.Model):
    type_name = models.CharField(max_length=25)

    def __str__(self):
        return self.type_name

    @staticmethod
    def get_default_pk():
        tagtype, created = TagType.objects.get_or_create(
            type_name='other',
        )
        return tagtype.pk


class Tag(models.Model):
    shareddata = models.OneToOneField(
        SharedData,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="linked_tag",
    )
    # foreign key relationship to list of approved tag types
    tag_type = models.ForeignKey(TagType, on_delete=models.SET_DEFAULT, default=TagType.get_default_pk)
    # relationship to self for appending closely related tags to search queries
    related_search_tags = models.ManyToManyField('self', symmetrical=False)
    
    def __str__(self):
        return self.shareddata.main_name
    
    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        sdata = self.shareddata
        if not hasattr(sdata, "linked_creator") and not hasattr(sdata, "linked_project"):
            sdata.delete() #this should take out itself as well
        else:
            super().delete(*args, **kwargs)
    

class Creator(models.Model):
    # choices for creator_type
    # a person can be a member of a group; a group has members AND can be part of a larger group
    # when unknown, will have to check for members AND groups (--same behaviour as if it were a group)
    TYPE_UNKNOWN = 0; TYPE_PERSON = 1; TYPE_GROUP = 2; TYPE_BOTH = 3
    CREATOR_TYPE_CHOICES = [
        (TYPE_UNKNOWN, "unknown"), 
        (TYPE_PERSON, "person"), 
        (TYPE_GROUP, "group"), 
        (TYPE_BOTH, "person & group"),
    ]

    shareddata = models.OneToOneField(
        SharedData,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="linked_creator",
    )
    creator_type = models.SmallIntegerField(choices=CREATOR_TYPE_CHOICES, default=TYPE_UNKNOWN)
    # relationship to self made to allow the concept of things like studios
    circles = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='CreatorCircle',
        through_fields=('creator', 'circle'),
        related_name="circle_members",
    )
    content_tags = models.ManyToManyField(Tag, related_name="content_creators")

    def __str__(self):
        return self.shareddata.main_name
    
    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        sdata = self.shareddata
        if not hasattr(sdata, "linked_tag") and not hasattr(sdata, "linked_project"):
            sdata.delete() #this should take out itself as well
        else:
            super().delete(*args, **kwargs)


class Project(models.Model):
    shareddata = models.OneToOneField(
        SharedData,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="linked_project",
    )
    overall_score = models.FloatField(null=True)
    release_date = models.DateField(null=True)
    last_update_date = models.DateField(null=True)
    # many-to-many relationships for getting a list of related tags and creators
    tags = models.ManyToManyField(Tag, through='ProjectTagInfo')
    creators = models.ManyToManyField(Creator, through='CreatorProjectContribution')
    # related projects/series (groups of projects)
    related_series = models.ManyToManyField("ProjectSeries", through="ProjectSeriesEntry")
    other_related_projects = models.ManyToManyField("self")

    def __str__(self):
        return self.shareddata.main_name
    
    def get_content_creators(self):
        return self.shareddata.linked_tag.content_creators.all().select_related("shareddata")

    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        # delete the SharedData object if nothing else references it
        sdata = self.shareddata
        if not hasattr(sdata, "linked_tag") and not hasattr(sdata, "linked_creator"):
            sdata.delete() #this should take out itself as well
        else:
            super().delete(*args, **kwargs)
    

class ProjectSeries(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    def get_entries(self):
        return ProjectSeriesEntry.objects.filter(projectseries=self)
    
    def get_entry(self, project_id):
        return ProjectSeriesEntry.objects.get(projectseries=self, project=project_id).order_num
    

# defined many-to-many tables in order to add extra column(s) containing more information
class ProjectSeriesEntry(models.Model):
    DEFAULT_ORDER_NUM = -1024

    projectseries = models.ForeignKey(ProjectSeries, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    order_num = models.FloatField(default=DEFAULT_ORDER_NUM)

    def __str__(self):
        return f"{self.order_num}||{self.projectseries.name}||{self.project.shareddata.main_name}"

    def calc_order_num(self, adjacent_entry, relative_position):
        try:
            all_entries_in_series = ProjectSeriesEntry.objects.filter(
                projectseries=self.projectseries
            ).exclude(pk=self.pk).exclude(
                order_num=ProjectSeriesEntry.DEFAULT_ORDER_NUM
            ).order_by("order_num")
            num_entries = len(all_entries_in_series)
            if num_entries == 0:
                return 0
            else:
                prev_order_num = None
                for index in range(0, num_entries):
                    current_entry = all_entries_in_series[index]
                    current_order_num = current_entry.order_num
                    if current_entry == adjacent_entry:
                        # edge cases (literally at the edge of the array)
                        if index == 0 and relative_position == "before":
                            return current_order_num - 1
                        if index == num_entries - 1 and relative_position == "after":
                            return current_order_num + 1
                        # all other cases which take place in the middle
                        if relative_position == "before":
                            return (prev_order_num + current_order_num) / 2
                        if relative_position == "after":
                            next_order_num = all_entries_in_series[index+1].order_num
                            return (current_order_num + next_order_num) / 2
                    prev_order_num = current_order_num        
            #return ProjectSeriesEntry.DEFAULT_ORDER_NUM #something went wrong, return default
        except:
            pass
        return ProjectSeriesEntry.DEFAULT_ORDER_NUM #something went wrong, return default
    
    def save(self, *args, **kwargs):
        being_created = (self.pk == None)
        adj_entry = kwargs.get('adj_entry')
        rel_pos = kwargs.get('rel_pos')
        if being_created or (adj_entry != None and rel_pos != None):
            self.order_num = self.calc_order_num(adj_entry, rel_pos)
        if adj_entry != None:
            kwargs.pop("adj_entry")
        if rel_pos != None:
            kwargs.pop("rel_pos")
        return super().save(*args, **kwargs)


class ProjectTagInfo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    score = models.FloatField(null=True)
    num_votes = models.PositiveIntegerField(default=0)

class CreatorProjectContribution(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creator =  models.ForeignKey(Creator, on_delete=models.CASCADE)
    role_info = models.CharField(max_length=10)

class CreatorCircle(models.Model):
    circle = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='members')
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='joined_circles')
    role_info = models.CharField(max_length=10)

#################################################################################
#################################################################################


#################################################################################
# Voting
#################################################################################
class OverallProjectScoreBallot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uid_hash = models.BinaryField(max_length=32)
    uid_salt = models.BinaryField(max_length=16, null=True)
    score = models.SmallIntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(10)])
    submitted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"id={self.pk}||{self.project}||{self.score}/10"
#################################################################################
#################################################################################


#################################################################################
# Edits System
#################################################################################
class EditRequestManager(models.Manager):
    use_in_migrations = True

    def create_editrequest(self, title, description):
        current_time = timezone.now()
        editrequest = self.create(
            title=title,
            description=description, 
            created_date=current_time, 
            voting_ends_date=current_time+datetime.timedelta(days=7)
        )
        return editrequest

class EditRequest(models.Model):
    created_date = models.DateTimeField("submitted on")
    voting_ends_date = models.DateTimeField("voting ends on")
    evaluation_date = models.DateTimeField("evaluated on", null=True, blank=True)
    evaluation_result = models.CharField(max_length=10) #'Accepted' or 'Rejected'
    title = models.CharField(max_length=50, default="New Request")
    description = models.CharField(max_length=250)
    votes = models.IntegerField(default=0)
    
    objects = EditRequestManager()
    
    def __str__(self):
        return self.title
    
    def will_push_early(self):
        if (self.votes >= 100) and ((timezone.now() - self.created_date) > datetime.timedelta(minutes=5)):
            return True
        else:
            return False


class EditRequestComment(models.Model):
    edit_request = models.ForeignKey(EditRequest, on_delete=models.CASCADE)
    pro_con_text = models.CharField(max_length=100)
    pro_con_type = models.SmallIntegerField(default=0) #PRO=1, CON=-1
    upvotes = models.IntegerField(default=0)

    def __str__(self):
        return f'({self.pro_con_type}, {self.pro_con_text})'

#################################################################################