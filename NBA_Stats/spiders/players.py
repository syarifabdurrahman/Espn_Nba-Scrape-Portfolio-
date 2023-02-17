import scrapy
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod


class PlayersSpider(scrapy.Spider):
    name = 'players'
    allowed_domains = ['www.nba.com', 'www.espn.com']

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.espn.com/nba/stats/player/_/season/2023/seasontype/2',
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_coroutines=[
                    PageMethod('click',
                               '//a[@class="AnchorLink loadMore__link"]'),
                    PageMethod('wait_for_selector',
                                "//table[@class='Table Table--align-right Table--fixed Table--fixed-left']//tbody//tr"),
                ]
            ),
            callback=self.parse,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        page.set_default_timeout(1000)
        button = page.locator("xpath=//a[@class='AnchorLink loadMore__link']")
        try:
            while button := page.locator("//div[contains(@class,'loadMore')]/a"):
                await button.scroll_into_view_if_needed()
                await button.click()
        except:
            pass
        content = await page.content()
        sel = Selector(text=content)

        player_list = sel.xpath("//table[@class='Table Table--align-right Table--fixed Table--fixed-left']//tbody//tr")
        stats_list = sel.xpath("//div[@class='Table__ScrollerWrapper relative overflow-hidden']/div[@class='Table__Scroller']/table/tbody/tr")

        for player, stat in zip(player_list, stats_list):
            player_name = player.xpath(".//a/text()").get()
            position = stat.xpath(".//td/div/text()").get()
            team_name = player.xpath(".//span/text()").get()
            game_played = stat.xpath(".//td[2]/text()").get()
            minutes_per_minute = stat.xpath(".//td[3]/text()").get()
            points_per_game = stat.xpath(".//td[4]/text()").get()
            fields_goal_made = stat.xpath(".//td[5]/text()").get()
            fields_goal_attempted = stat.xpath(".//td[6]/text()").get()
            field_goal_percentage = stat.xpath(".//td[7]/text()").get()
            three_point_goal_made = stat.xpath(".//td[8]/text()").get()

            yield {
                "player_name": player_name,
                "player_position": position,
                "team_name": team_name,
                "game_played": game_played,
                "minutes_per_minute": minutes_per_minute,
                "points_per_game": points_per_game,
                "fields_goal_made": fields_goal_made,
                "fields_goal_attempted": fields_goal_attempted,
                "field_goal_percentage": field_goal_percentage,
                "three_point_goal_made": three_point_goal_made,
            }
        