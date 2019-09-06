# Ideas for Future Improvement

## Location Scraping
* Search for the word "address" nearby the found postalcodes
* Look specifically in the footer for the address, since many sites put them here
* Prioritize certain links on the main page that have the word "contact" in them. For example, "contact us" is probably what we want, and other links might be random
* Right now, we always visit the "contact" page before looking on the main page itself. This has led to problems at least once, when the main page had the address but the contact page had something else that got found. Might do this more intelligently
* Could also visit the actual homepage of the site, which might be more accurate than the page itself (for example, many sites list the addresses of many organizations on them. For consistency, it might make more sense to always try to find the address of the home site itself).
* Could check whether a country is actually listed as part of the address, which would eliminate the guessing at which country the postalcode is for. So far, I haven't seen many addresses displaying country though.
* Right now, I'm adding all countries in which the page language is spoken to the list of country guesses. This is dumb when it comes to languages that are spoken in many, many countries (English, Spanish, French, etc).
* Would be good to provide some sort of confidence estimate on location.
* Right now, the first coordinate found is just returned. It would be better to find all possible ones, give them different rankings, and pick the most likely.
* Holding dictionaries in memory for the entire life of the server is dumb. Started doing this when I was creating HUGE dictionaries (12 million entries), but it is no longer necessary. They should either be recreated when necessary or pulled from a file or database

## UI
* It would be nice to have some sort of visual link between the two markers for a site. Like, when you mouse over one, the other is highlighted.
* A favicon!
