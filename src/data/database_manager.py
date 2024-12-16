from peewee import SqliteDatabase
from peewee import fn
from src.models.models import Page, Contributor, Revision, MainCategory, Crawls

class DatabaseManager:
    def __init__(self,db):
        self.db = db
        if self.db.is_closed():
            self.db.connect()
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Ensure the database tables are created."""
        self.db.create_tables([Page, Contributor, Revision, MainCategory, Crawls], safe=True)

    def get_or_create_page(self, page_id, page_name):
        page, created = Page.get_or_create(id=page_id, defaults={'name': page_name})
        return page

    def get_or_create_contributor(self, username):
        contributor, created = Contributor.get_or_create(username=username)
        return contributor

    def create_revision(self, revision_id, page, contributor, timestamp, main_category_id):
        revision, created = Revision.get_or_create(
            id=revision_id,
            defaults={
                'page': page,
                'contributor': contributor,
                'timestamp': timestamp,
                'main_category': main_category_id
            }
        )
        return revision

    def get_or_create_main_category(self, category_name):
        main_category, created = MainCategory.get_or_create(
            name=category_name,
        )
        return main_category
    
    def update_main_category(self, category_name, num_subcategories):
        main_category = MainCategory.get(name=category_name)
        main_category.number_of_subcategories = num_subcategories
        main_category.save()
        return main_category

    def create_crawl(self, main_category, depth, start_time, end_time):
        crawl = Crawls.create(
            main_category=main_category,
            depth=depth,
            start_time=start_time,
            end_time=end_time
        )
        return crawl

    def get_all_crawls(self):
            return Crawls.select()

    def get_all_revisions(self):
        return Revision.select()

    def get_all_pages(self):
        return Page.select()

    def get_all_contributors(self, main_category_id=None):
        if main_category_id:
            return (
                Contributor.select()
                .join(Revision)
                .where(Revision.main_category == main_category_id)
                .distinct()
            )
        else:
            return Contributor.select()

    def get_all_categories(self):
        return MainCategory.select()

    def delete_category_by_id(self, category_id):
        MainCategory.delete().where(MainCategory.id == category_id).execute()

    def delete_crawl_by_id(self, crawl_id):
        Crawls.delete().where(Crawls.id == crawl_id).execute()

    def update_crawl(self, crawl_id, main_category_id):
        crawl = Crawls.get(id=crawl_id)
        crawl.main_category = main_category_id
        crawl.save()
        return crawl

    def get_unique_stats_per_month(self, main_category_id):
        """Get unique contributors and pages per month, optionally filtered by main_category_id, as a Pandas DataFrame."""
        from peewee import fn

        query = (
            Revision
            .select(
                fn.strftime('%Y-%m', Revision.timestamp).alias('month'),  # Extract year and month
                fn.COUNT(Revision.id).alias('total_contributions'),
                fn.COUNT(fn.DISTINCT(Revision.page)).alias('unique_pages'),
                fn.COUNT(fn.DISTINCT(Revision.contributor)).alias('unique_contributors')
            )
            .group_by(fn.strftime('%Y-%m', Revision.timestamp))
            .order_by(fn.strftime('%Y-%m', Revision.timestamp))
        )
    
        query = query.where(Revision.main_category == main_category_id)

        results = list(query.dicts())

        df = pd.DataFrame(results)

        if not df.empty:
            df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

        return df

    def get_co_contributors(self, contributor_id):
        """Get co-contributors' IDs for a given contributor_id."""
        RevisionAlias = Revision.alias()

        query = (
            RevisionAlias
            .select(RevisionAlias.contributor, fn.COUNT(RevisionAlias.id).alias('contribution_count'))
            .join(Revision, on=(RevisionAlias.page == Revision.page))
            .where(
                (Revision.contributor == contributor_id) &
                (RevisionAlias.contributor != contributor_id) 
            )
            .group_by(RevisionAlias.contributor)
            .order_by(fn.COUNT(RevisionAlias.id).desc())
        )

        return [row.contributor.id for row in query]

    def close(self):
        if not self.db.is_closed():
            self.db.close()


