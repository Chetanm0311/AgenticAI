import requests
from bs4 import BeautifulSoup
from msal_auth import GPT_Model
import json
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


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
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

    def summarize(self,ai_model, max_length=100):
        """
        Summarize the text of this Website object to a maximum length of max_length characters
        """
        context = messages_for(self)
        summary = ai_model.chat(context)
        print(summary)


if __name__ == "__main__":
    openai = GPT_Model()
    website = Website("https://www.pypi.org/")
    print(website.text)
    website.summarize(ai_model=openai)
    
    

    


        
