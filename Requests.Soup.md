# BeautifulSoup4 snippets

## `.find_all( fn )` to filter by attribute

```python
def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

results = soup.find_all(has_class_but_no_id)
```