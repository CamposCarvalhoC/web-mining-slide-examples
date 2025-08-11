import scrapy
import networkx as nx
from urllib.parse import urljoin, urlparse
import matplotlib.pyplot as plt
import random

class ExtractPdf(scrapy.Spider):
    name = "extract_linkgraph"
    main_url = "https://www.hes-so.ch"
    max_depth = 2
    max_links_per_page = 2
    link_graph = nx.DiGraph()

    async def start(self):
        url = f"{ExtractPdf.main_url}/plan-du-site"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, depth = 0):
        if depth > ExtractPdf.max_depth:
            return # stop recursion
        
        source_url = response.url
        try:
            main_content = response.css("div#content")
            urls = main_content.css("a::attr(href)").getall()
            print(f"Found {len(urls)} links on {source_url} at depth {depth}, max {ExtractPdf.max_links_per_page} links per page.")
            for url in random.sample(urls,min(ExtractPdf.max_links_per_page, len(urls))):
                absolute_url = urljoin(self.main_url, url)
                
                # Add nodes & edge to the graph
                self.link_graph.add_node(source_url)
                self.link_graph.add_node(absolute_url)
                self.link_graph.add_edge(source_url, absolute_url)
                
                # Continue crawling if in domain and not too deep
                if self.main_url in absolute_url:
                    yield scrapy.Request(url=absolute_url, callback=self.parse, cb_kwargs={"depth": depth + 1})
        except scrapy.exceptions.NotSupported:
            print(f"Skipping unsupported URL: {source_url}")


    def add_newlines_to_path(self, path):
        parts = path[1:].split('/') # skips first slash
        return '/\n'.join(parts)
    

    def closed(self, reason):
        '''
        This method is called when the spider is closed.
        Made with the help of ChatGPT.
        '''
        # Calculate depth for each node
        depths = {}
        start_node = f"{self.main_url}/plan-du-site"
        for node in self.link_graph.nodes():
            try:
                depths[node] = nx.shortest_path_length(self.link_graph, source=start_node, target=node)
            except nx.NetworkXNoPath:
                depths[node] = None

        # Position nodes by depth
        pos = {}
        levels = {}
        for node, depth in depths.items():
            if depth is None:
                depth = 0
            levels.setdefault(depth, []).append(node)

        for depth, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = (i, -depth)

        plt.figure(figsize=(12, 8))

        nx.draw_networkx_edges(self.link_graph, pos, alpha=0.4, arrows=True)

        labels = {
            n: self.add_newlines_to_path(urlparse(n).path)
            for n in self.link_graph.nodes()
        }
        nx.draw_networkx_labels(self.link_graph, pos, labels=labels, font_size=8)

        plt.axis("off")
        plt.tight_layout()
        plt.savefig("data/link_graph.png", dpi=300)
        plt.close()
