from bs4 import BeautifulSoup
import os
import re
import sys


html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/styles.css">
    <script>
        function toggleResult(event)
        {
            const parentNode = event.target.parentNode;
            let preTag = parentNode.getElementsByTagName("pre")[0];

            if (preTag.style.display == "none") {
                preTag.style.display = "block";
            } else {
                preTag.style.display = "none";
            }

        }
    </script>
    <title></title>
</head>
<body>
<div class="content">
    <div class="project"></div>
    <div class="result-container"></div>
</div>
</body>
</html>
'''

SRC_DIR = "../src"
HTML_DIR = "../questions"


def save_html_file_content(resulting_html_structure_dir, directory_name, content):
    html_file_path = os.path.join(resulting_html_structure_dir, directory_name + ".html")
    print(html_file_path)
    print(os.path.dirname(html_file_path))
    if not os.path.isdir(os.path.dirname(html_file_path)):
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

    with open(html_file_path, "w") as html_file:
        html_file.write(content.prettify())

def parse_readme(readme_file_path, result_container, soup):
    with open(readme_file_path) as readme:
        content = readme.read()
        result_container.append(create_godbolt_link(content, soup))
        # result_container.append(create_result_img(content, soup))
        result_container.append(create_result_value(content, soup))

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
    result_value = soup.new_tag('div')
    result_value['class'] = 'result-value'

    result_title = soup.new_tag('div')
    result_title.string = 'Result:'
    result_title['class'] = 'result-title'
    result_title['onclick'] = 'toggleResult(event)'
   
    result = re.search("(```)([ ]*\n)([\s\S]*?)(?=```)", readme_content)
    pre = soup.new_tag('pre')
    pre['style'] = 'display: none'
    pre.string = result.group(3)

    result_value.append(result_title)
    result_value.append(pre)

    return result_value

def create_HTML_structure_for_cpp_projects(cpp_sources_dir, resulting_html_structure_dir):
    for root, dirs, files in os.walk(cpp_sources_dir, topdown=False):
        is_dir_with_files = False
        if root == cpp_sources_dir:
            continue
        
        soup = BeautifulSoup(html_template, "html.parser")
        project = soup.find_all("div", class_="project")[0]
        result_container = soup.find_all("div", class_="result-container")[0]

        # print(root, dirs, files)
        for name in files:
            is_dir_with_files = True

            file_path = os.path.join(root, name)

            if name == "README.md":
                parse_readme(file_path, result_container, soup)
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

        directory_name = os.path.relpath(root, cpp_sources_dir)
        # button
        # report_btn = soup.new_tag('button')
        # report_btn['class'] = 'report'
        # report_btn.string = 'Report'
        # soup.append(report_btn)

        if is_dir_with_files:
            save_html_file_content(resulting_html_structure_dir, directory_name, soup)    


if __name__ == "__main__":
    cpp_sources_dir = SRC_DIR
    resulting_html_structure_dir = HTML_DIR

    if len(sys.argv) == 3:
        cpp_sources_dir = sys.argv[1]
        resulting_html_structure_dir = sys.argv[2]
    elif len(sys.argv) != 1:
        print("Wrong number of arguments! parser.py [cpp_sources_dir] [resulting_html_structure_dir]")
        exit(-1)
    
    create_HTML_structure_for_cpp_projects(cpp_sources_dir, resulting_html_structure_dir)

