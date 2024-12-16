from peewee import SqliteDatabase, Model, IntegerField, CharField, ForeignKeyField, DateTimeField
from datetime import datetime
from data.db.database import db


class BaseModel(Model):
    class Meta:
        database = db

class Page(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True, null=False)

    def to_dict(self):
        number_of_revisions = Revision.select().where(Revision.page == self).count()
        number_of_contributors = Revision.select().where(Revision.page == self).distinct().count()

        return {
            "id": self.id,
            "name": self.name,
            "number_of_revisions": number_of_revisions,
            "number_of_contributors": number_of_contributors,
        }

class Contributor(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(unique=True, null=False)

    def to_dict(self):
        number_of_pages = Page.select().join(Revision).where(Revision.contributor == self).distinct().count()
        number_of_contributions = Revision.select().where(Revision.contributor == self).count()

        return {
            "id": self.id,
            "username": self.username,
            "number_of_pages": number_of_pages,
            "number_of_contributions": number_of_contributions,
        }

class MainCategory(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True, null=False)
    number_of_subcategories = IntegerField(null=True)

    def to_dict(self):
        number_of_pages = Page.select().join(Revision).where(Revision.main_category == self).distinct().count()

        number_of_contributors = (
            Contributor.select()
            .join(Revision)
            .where(Revision.main_category == self)
            .distinct()
            .count()
        )

        number_of_contributions = Revision.select().where(Revision.main_category == self).count()

        return {
            "id": self.id,
            "name": self.name,
            "number_of_subcategories": self.number_of_subcategories,
            "number_of_pages": number_of_pages,
            "number_of_contributors": number_of_contributors,
            "number_of_contributions": number_of_contributions,
        }


class Revision(BaseModel):
    id = IntegerField(primary_key=True)
    main_category = ForeignKeyField(MainCategory, backref='revisions', on_delete='CASCADE')
    page = ForeignKeyField(Page, backref='revisions', on_delete='CASCADE')
    contributor = ForeignKeyField(Contributor, backref='revisions', on_delete='CASCADE')
    timestamp = DateTimeField(default=datetime.utcnow)

    class Meta:
        indexes = (
            (('id', 'main_category'), True),  # Composite unique index
        )

    def to_dict(self):
        return {
            "id": self.id,
            "main_category": self.main_category.name,
            "page": self.page.name,
            "contributor": self.contributor.username,
            "timestamp": self.timestamp,
        }

class Crawls(BaseModel):
    id = IntegerField(primary_key=True)
    main_category = ForeignKeyField(MainCategory, backref='crawls', on_delete='CASCADE')
    depth = IntegerField()
    start_time = DateTimeField()
    end_time = DateTimeField()

    def to_dict(self):
        return {
            "id": self.id,
            "main_category": self.main_category.name,
            "depth": self.depth,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
