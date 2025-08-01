import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from msal_auth import GPT_Model
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
                    Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

def get_links_system_prompt():
    link_system_prompt = "You are provided with a list of links found on a webpage. \
                          You are able to decide which of the links would be most relevant to include in a brochure about the company, \
                          such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    link_system_prompt += "You should respond in JSON as in this example:"
    link_system_prompt += """
                        {
                            "links": [
                                {"type": "about page", "url": "https://full.url/goes/here/about"},
                                {"type": "careers page": "url": "https://another.full.url/careers"}
                            ]
                        }
                    """
    return link_system_prompt

def get_links(model,url):
    website = Website(url)
    response = model.chat(
        chat_msg=[
            {"role": "system", "content": get_links_system_prompt()},
            {"role": "user", "content": get_links_user_prompt(website)}
      ]
        # response_format={"type": "json_object"}
    )
    print(response.json())
    # result = response.choices[0].message.content
    return response.json()

def get_all_details(model,url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(model,url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

class Website:
    
    proxies = {
        "http":"",
        "https":"",
        
    }
    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers,verify=False,proxies=self.proxies,timeout=30)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
class Broucher:
    
    system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
                    and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
                    Include details of company culture, customers and careers/jobs if you have the information."
    
    def __init__(self,model,company_name,url):
        self.model = model
        self.company_name = company_name
        self.url = url

    def get_brochure_user_prompt(self):
        user_prompt = f"You are looking at a company called: {self.company_name}\n"
        user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
        user_prompt += get_all_details(self.model,self.url)
        user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
        return user_prompt
    
    def create_brochure(self):
        response = self.model.chat(
            
            chat_msg=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.get_brochure_user_prompt()}
            ],
        )
        result = response.text
        print(result)
        # display(Markdown(result))

if __name__ == "__main__":
    openai = GPT_Model()
    # website = Website("https://www.pypi.org/")
    # print(website.links)
    # website.get_contents()
    # details = get_all_details(openai,"https://www.pypi.org/")
    b = Broucher(openai,"HuggingFace","https://huggingface.co")
    b.create_brochure()
