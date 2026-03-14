# coding:utf-8

import datetime
import requests
import os
import sqlite3
import time
from pyquery import PyQuery as pq


def git_add_commit_push(date, filename):
    cmd_git_add = 'git add {filename}'.format(filename=filename)
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


def createMarkdown(date, filename):
    with open(filename, 'w') as f:
        f.write("## " + date + "\n")


def scrape(language, filename, db_path="trending.db"):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200

    d = pq(r.content)
    items = d('div.Box article.Box-row')

    conn = sqlite3.connect(db_path) if os.path.exists(db_path) else None

    # codecs to solve the problem utf-8 codec like chinese
    with open(filename, "a", encoding="utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)

            if conn:
                repo_slug = url.replace("https://github.com/", "").lstrip("/")
                cursor = conn.execute(
                    "SELECT COUNT(DISTINCT date) FROM trending_repos WHERE repo_slug = ?",
                    (repo_slug,)
                )
                count = cursor.fetchone()[0]
                meta = " [first time]" if count == 0 else " [seen {count}x]".format(count=count)
            else:
                meta = ""

            f.write(u"* [{title}]({url}):{description}{meta}\n".format(
                title=title, url=url, description=description, meta=meta))

    if conn:
        conn.close()


def job(db_path="trending.db"):
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=strdate)

    # create markdown file
    createMarkdown(strdate, filename)

    # write markdown
    scrape('python', filename, db_path)
    scrape('swift', filename, db_path)
    scrape('javascript', filename, db_path)
    scrape('go', filename, db_path)

    # git add commit push
    # git_add_commit_push(strdate, filename)


if __name__ == '__main__':
    job()
