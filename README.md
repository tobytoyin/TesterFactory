# TesterFactory

# Action-functions & their Validate-functions Example

## 1. Lookup

**checkout**: Lookup whether a web-element exist or not.  
**checkout_validate**: Based on the lookup result, `checkout_validate` generates result passed on below matrix:

|     Scenario      | Validate Input | Output |
| :---------------: | :------------: | :----: |
| Element Exist > 0 |      Yes       |  Pass  |
| Element Exist = 0 |      Yes       |  Fail  |
| Element Exist > 0 |       No       |  Fail  |
| Element Exist = 0 |       No       |  Pass  |

## 2. URL related functions

**goto**: webdriver will travel to a specific page/ object

|      Scenario       |  logic   |   Required (field)   |
| :-----------------: | :------: | :------------------: |
| (default) goto url  |          |   a url-link (key)   |
| click return button |  --back  |         None         |
|     goto iframe     | --iframe | a iframe path (path) |

## 2. Button related functions

### validation

**redirect_validate**: Validate whether the browser redirect to an expected url.

|             Scenario             | Validate Input | validate-logic |               Example               | Output |
| :------------------------------: | :------------: | :------------: | :---------------------------------: | :----: |
| url contains \<input> in the url |     string     |   --contain    | https://www.sample.com/string-input |  Pass  |

## N. Waiting functions

**wait**: Specified n-seconds for the webdriver to wait.
-- default: 5 sec
`for(n)`: `n` should be a `int`, wait for `n` sec
