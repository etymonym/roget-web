from django.db.models import                        \
Model, Manager,                                     \
ForeignKey, ManyToManyField, CASCADE,               \
CharField, TextField, DateTimeField, BooleanField,  \
UniqueConstraint, CheckConstraint, Q, F

from django.contrib.auth.models import User
from django.utils import timezone

class Collection(Model):

    # Every collection has a User
    user = ForeignKey(User, on_delete = CASCADE)

    # Every collection is given a Name
    name = CharField(max_length = 80)

    # Every collection is created at a specific time
    date_created = DateTimeField("Date Created")

    # Every collection keeps track of when it was last modified
    last_modified = DateTimeField("Last Modified")

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.user == other.user and self.name == other.name
    
    def __hash__(self):
        return hash((self.user.username,self.name))

    def change_name(self, new_name):
        self.name = new_name

    class Meta:
        abstract = True

        # By default, collections of a given kind will order 
        # themselves according to when they were created
        # First -> Last : Most Recent -> Least Recent
        ordering = ["date_created"]

        constraints = [

            # All collections of a given kind must have
            # names which are unique relative to their user
            UniqueConstraint(fields = ["user","name"], name = "%(class)s_unique_name"),

            # Checks to make sure the date of last modification
            # is always after or equal to the date of creation
            CheckConstraint(check = Q(date_created__lte = F("last_modified")), name = "%(class)s_causality"),
        ]

class LexiconManager(Manager):

    # Creates a new Lexicon
    def create_lexicon(self, user, name):

        # Set the Lexicon's creation and last modified time 
        date_created = last_modified = timezone.now()

        # Create
        lexicon = Lexicon(
            user = user,
            name = name,
            date_created = date_created,
            last_modified = last_modified,
        )

        # Save 
        lexicon.save()

        return lexicon

class Lexicon(Collection):

    objects = LexiconManager()

    def add_lexeme(self, text):

        # Update the Lexicon's last modified time to the Lexeme's added time
        self.last_modified = date_added = timezone.now()

        # Save the update
        self.save()

        # Create the Lexeme
        lexeme = Lexeme(
            lexicon = self,
            text = text,
            date_added = date_added,
        )

        # Save it
        lexeme.save()

        return lexeme

    def remove_lexeme(self, lexeme):

        # Update the Lexicon's last modified time
        self.last_modified = timezone.now()

        # Save the update
        self.save()

        # Delete the Lexeme
        self.lexeme_set.get(pk = lexeme.pk).delete()

class WebManager(Manager):

    # Creates a new Web
    def create_web(self, user, name):

        # Set the Web's creation and last modified time 
        date_created = last_modified = timezone.now()

        # Create the Web
        web = Web(
            user = user,
            name = name,
            date_created = date_created,
            last_modified = last_modified,
        )

        # Save it
        web.save()

        return web

class Web(Collection):

    objects = WebManager()

    def add_relation(self, name, source, sink):
        
        # Update the Web's last modified time to the Relation's added time
        self.last_modified = date_added = timezone.now()

        # Save the update
        self.save()

        # Create the Relation
        relation = Relation(
            web = self,
            name = name,
            source = source,
            sink = sink,
            date_added = date_added,
        )
        
        # Save it
        relation.save()

        return relation

    def remove_relation(self, relation):

        # Update the Web's last modified time
        self.last_modified = timezone.now()

        # Delete the Relation
        self.relation_set.get(pk = relation.pk).delete()

class Item(Model):

    # Each item is added to its collection at a specific time
    date_added = DateTimeField("Date Added")

    class Meta:
        abstract = True

        # By default, items of a given kind will order 
        # themselves according to when they were added
        # First -> Last : Most Recent -> Least Recent
        ordering = ["date_added"]

# Smallest unit of meaning
class Lexeme(Item):

    # Each Lexeme belongs to a Lexicon
    lexicon = ForeignKey(Lexicon, on_delete = CASCADE)
    
    # Each Lexeme has some text as its primary content
    text = TextField()

    # Lexemes can be related to many other Lexemes
    relations = ManyToManyField(
        "self", 
        symmetrical = False,
        through = "Relation",
        through_fields = ("source","sink"),
    )

    class Meta:

        # Lexemes are sorted alphabetically by their text
        ordering = ["text"]

        # A Lexeme's text must be unique relative to it's Lexicon
        constraints = [
            UniqueConstraint(fields = ["lexicon","text"], name = "unique_lexeme")
        ]

    def __str__(self):
        return self.text

    # Comparison methods for Lexemes are defined irrespective of their Lexicon
    def __eq__(self, other):
        return self.text == other.text
    
    def __lt__(self, other):
        return self.text < other.text

    def __hash__(self):
        return hash(self.text)

# Directed connections between two lexemes via a third
class Relation(Item):

    # Each Relation belongs to a Web
    web = ForeignKey(Web, on_delete = CASCADE)

    # Each Relation has a Name as well as a Source & Sink
    # All three of which are some Lexeme
    name = ForeignKey(Lexeme, related_name="relation_name", on_delete = CASCADE )
    source = ForeignKey(Lexeme, related_name="source", on_delete = CASCADE )
    sink = ForeignKey(Lexeme, related_name="sink", on_delete = CASCADE )

    # A Relation can be Directed from Source to Sink
    # or it can be Symmetric between them
    symmetric = BooleanField(default = False)

    class Meta:

        constraints = [

            # A Relation's Name, Source, and Sink must together be unique
            # relative to their Web
            UniqueConstraint(fields = ["web","name","source","sink"], name = "unique_relation"),

        ]

        # Relations are by default ordered alphabetically by Name
        # then most to least recent by the date they were added
        # and finally alphabetically by their Source
        ordering = ["name","date_added","source"]


    def __str__(self):
        if self.symmetric:
            return "".join([self.source.text, " ←{ ", self.name.text, " }→ ", self.sink.text])
        return "".join([self.source.text, " ─{ ", self.name.text, " }→ ", self.sink.text]) 

    # Comparison methods for Relations are defined irrespective of their Web
    def __eq__(self, other):
        return self.name == other.name and self.source == other.source and self.sink == other.sink
    
    def __hash__(self):
        return hash((self.name.text,self.source.text,self.sink.text))

    
