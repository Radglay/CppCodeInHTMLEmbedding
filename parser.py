from bs4 import BeautifulSoup
import os
import re


html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/styles.css">
    <script src='http://alexgorbatchev.com/pub/sh/current/scripts/shBrushCpp.js' type='text/javascript'/>
    <title></title>
</head>
<body>
<div class="content">
    <div class="project"></div>
    <div class="output"></div>
</div>
</body>
</html>
'''

SRC_DIR = "./src"

def save_html_file_content(directory_name, content):
    html_file_path = directory_name + ".html"
    with open(html_file_path, "w") as html_file:
        html_file.write(content.prettify())

def parse_readme(readme_file_path, output, soup):
    with open(readme_file_path) as readme:
        content = readme.read()
        output.append(create_godbolt_link(content, soup))
        # output.append(create_result_img(content, soup))
        output.append(create_result_value(content, soup))

def create_godbolt_link(readme_content, soup):
    result = re.search("([\* ])*(godbolt)([\* ])*:[ ]*(https:\/\/godbolt\.org.*)", readme_content)
    godbolt_link = soup.new_tag("a")
    godbolt_link['class'] = 'online-compiler-link'
    godbolt_link['href'] = result.group(4)
    godbolt_link.string = 'online-compiler-link'
    return godbolt_link

# def create_result_img(readme_content, soup):
#     result = re.search("([\* ])*(result)([\* ])*:[ ]*.*(https:\/\/github\.com.*?(?=\)))", readme_content)
#     result_img = soup.new_tag("img")
#     result_img['class'] = 'result-img'
#     result_img['src'] = result.group(4)
#     return result_img

def create_result_value(readme_content, soup):
    result = re.search("(```)([ ]*\n)([\s\S]*?)(?=```)", readme_content)
    result_value = soup.new_tag('pre')
    result_value['class'] = 'result-value'
    result_value.string = result.group(3)
    return result_value

def create_HTML_structure_for_cpp_projects():
    for root, dirs, files in os.walk(SRC_DIR, topdown=False):
        if root == SRC_DIR:
            continue
        
        soup = BeautifulSoup(html_template, "html.parser")
        project = soup.find_all("div", class_="project")[0]
        output = soup.find_all("div", class_="output")[0]

        # print(root, dirs, files)
        for name in files:
            file_path = os.path.join(root, name)

            if name == "README.md":
                parse_readme(file_path, output, soup)
                continue

            pre = soup.new_tag("pre")
            code = soup.new_tag("code")

            with open(file_path) as file:
                code.string = file.read().strip()
            pre.append(code)


            file_container = soup.new_tag("div")

            if name.endswith('.cpp'):
                file_container['class'] = 'source'
            elif name.endswith('.h') or name.endswith('.hpp'):
                file_container['class'] = 'header'
            elif name == "CMakeLists.txt":
                file_container['class'] = 'cmake'
            else:
                file_container['class'] = 'misc'
            file_container['class'] += ' file'

            file_name_paragraph = soup.new_tag("p")
            file_name_paragraph['class'] = 'file-name'
            file_name_paragraph.string = name
    
            file_container.append(file_name_paragraph)
            file_container.append(pre)
            project.append(file_container)

        directory_name = os.path.relpath(root, SRC_DIR)
        # button
        # report_btn = soup.new_tag('button')
        # report_btn['class'] = 'report'
        # report_btn.string = 'Report'
        # soup.append(report_btn)

        save_html_file_content(directory_name, soup)    


if __name__ == "__main__":
    create_HTML_structure_for_cpp_projects()

