from peewee import SqliteDatabase
from peewee import fn
from src.acquisition.models.models import Page, Contributor, Revision, MainCategory, Crawls

class DatabaseManager:
    def __init__(self,db):
        self.db = db
        if self.db.is_closed():
            self.db.connect()
        self._ensure_tables_exist()
        self._create_index()

    def _ensure_tables_exist(self):
        """Ensure the database tables are created."""
        self.db.create_tables([Page, Contributor, Revision, MainCategory, Crawls], safe=True)
                

    def _create_index(self):
        with self.db.atomic():
            try:
                self.db.execute_sql('''
                    CREATE INDEX IF NOT EXISTS idx_revision_contributor_category 
                    ON revision (contributor_id, main_category_id)
                ''')
                self.db.execute_sql('''
                    CREATE INDEX IF NOT EXISTS idx_revision_page_category 
                    ON revision (page_id, main_category_id)
                ''')
            except Exception as e:
                print(f"Error creating indexes: {str(e)}")



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
        main_category = MainCategory.create(
            name=category_name
        )
        return main_category

    def get_main_category_by_name(self, category_name):
        """Get a main category by its name."""
        try:
            return MainCategory.get(MainCategory.name == category_name)
        except MainCategory.DoesNotExist:
            print(f"No category found with name '{category_name}'")
            return None
    
    def update_main_category(self, category_id, num_subcategories):
        main_category = MainCategory.get(id=category_id)
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

    def get_co_contributors(self, contributor_id, main_category_id):
        """Get unique co-contributors' IDs for a given contributor_id within the same main category."""
        pages_subquery = (
            Page
            .select(Page.id)
            .join(Revision)
            .where(
                (Revision.contributor == contributor_id) & 
                (Revision.main_category == main_category_id)
            )
            .distinct()
        )
        
        query = (
            Contributor
            .select(Contributor.id)
            .join(Revision)
            .where(
                (Revision.page.in_(pages_subquery)) & 
                (Contributor.id != contributor_id) &
                (Revision.main_category == main_category_id)
            )
            .distinct()
        )
        
        co_contributors = [contributor.id for contributor in query]
        return co_contributors

    def get_co_contributors_weighted(self, contributor_id, main_category_id):
        """
        Get co-contributors' IDs and their co-contribution counts for a given contributor_id.
        Returns a dictionary of {co_contributor_id: count}.
        """
        pages_subquery = (
            Page
            .select(Page.id)
            .join(Revision)
            .where(
                (Revision.contributor == contributor_id) &
                (Revision.main_category == main_category_id)
            )
            .distinct()
        )
        
        query = (
            Contributor
            .select(
                Contributor.id,
                fn.COUNT(Revision.id).alias('co_contribution_count')
            )
            .join(Revision)
            .where(
                (Revision.page.in_(pages_subquery)) &
                (Contributor.id != contributor_id) &
                (Revision.main_category == main_category_id)
            )
            .group_by(Contributor.id)
        )
        
        return {c.id: c.co_contribution_count for c in query}

    def get_distinct_contributors_per_page(self, main_category_id):
        """Get the number of distinct contributors per page for a given main category."""
        query = (
            Revision
            .select(
                Revision.page,
                fn.COUNT(fn.DISTINCT(Revision.contributor)).alias('distinct_contributors')
            )
            .where(Revision.main_category == main_category_id)
            .group_by(Revision.page)
        )
        
        return {r.page.id: r.distinct_contributors for r in query}

    def get_number_of_revisions_per_contributor(self, contributor_id, main_category_id):

        query = (
            Revision
            .select(
                fn.COUNT(Revision.id).alias('num_revisions')
            )
            .where(
                (Revision.contributor == contributor_id) &
                (Revision.main_category == main_category_id)
            )
        )
        return query.scalar()
    
    def get_total_number_of_revisions_per_main_category(self, main_category_id):
        query = (
            Revision
            .select(
                fn.COUNT(Revision.id).alias('num_revisions')
            )
            .where(Revision.main_category == main_category_id)
        )
        return query.scalar()
    
    def get_oldest_and_newest_revision_per_contributor_and_main_category(self, contributor_id, main_category_id):
        query = (
            Revision
            .select(
                fn.MIN(Revision.timestamp).alias('oldest_revision'),
                fn.MAX(Revision.timestamp).alias('newest_revision')
            )
            .where(
                (Revision.contributor == contributor_id) &
                (Revision.main_category == main_category_id)
            )
        )
        return query.dicts().get()
    
    def close(self):
        if not self.db.is_closed():
            self.db.close()


