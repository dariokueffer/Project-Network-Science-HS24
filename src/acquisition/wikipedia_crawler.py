from datetime import datetime, timezone
import mwclient
from tqdm import tqdm

class WikipediaCategoryCrawler():
    def __init__(self, main_category, db_manager):
        self.site = mwclient.Site('en.wikipedia.org')
        self.visited_categories = set()
        self.pages = set()
        self.contributors = set()
        self.contributions = set()

        self.main_category = main_category
        self.db_manager = db_manager

    def get_categories(self, depth=3):

        def get_subcategories(category, current_depth):
            if current_depth > depth or category in self.visited_categories:
                return []
            
            self.visited_categories.add(category)
            cat = self.site.categories[category]
            subcats = []

            for subcat in cat:
                if subcat.namespace == 14: # a namespace of 14 indicates a category, see reference below
                    subcat_name = subcat.name.replace('Category:', '')
                    subcats.append(subcat_name)
                    if current_depth < depth:
                        subcats.extend(get_subcategories(subcat_name, current_depth + 1))

            return subcats

        all_subcategories = get_subcategories(self.main_category, 1)
        
        print()
        print(f'Number of Subcategories: {len(all_subcategories)}')

        for idx, subcategory in enumerate(all_subcategories, start=1):
            print(f'Subcategory {idx}/{len(all_subcategories)}: {subcategory}')
            self.get_category_pages(subcategory)
            

    def get_category_pages(self, category):
        cat = self.site.categories[category]

        pages = [page for page in cat if page.namespace == 0]  # Collect only pages in namespace 0
        print()
        print(f"Number of pages in category '{category}': {len(pages)}")

        for page in tqdm(pages, desc="Processing Pages", unit="page"):
            tmp_page = self.db_manager.get_or_create_page(page_id=page.pageid, page_name=page.name)

            for revision in list(page.revisions()):
                if 'user' in revision:
                    tmp_contributor = self.db_manager.get_or_create_contributor(username=revision['user'])
                else:
                    tmp_contributor = self.db_manager.get_or_create_contributor(username="Unknown")

                timestamp_struct = revision['timestamp']
                timestamp_obj = datetime(*timestamp_struct[:6], tzinfo=timezone.utc)  # Convert struct_time to datetime
                formatted_timestamp = timestamp_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

                self.db_manager.create_revision(
                    revision_id=revision['revid'],
                    page=tmp_page,
                    contributor=tmp_contributor,
                    timestamp=formatted_timestamp,
                    main_category_id=self.main_category_id
                )

    def get_pages_and_contributions(self):
        self.get_category_pages(self.main_category)

    def crawl_category(self, depth=3):
        start_time = datetime.now(timezone.utc)
        self.main_category_id = self.db_manager.get_or_create_main_category(self.main_category)

        self.get_categories(depth)
        self.get_pages_and_contributions()


        end_time = datetime.now(timezone.utc)
        self.db_manager.create_crawl(
            main_category=self.main_category_id,
            depth=depth,
            start_time=start_time,
            end_time=end_time
        )

        self.db_manager.update_main_category(self.main_category_id, len(self.visited_categories))



