## Vinh Luong SI364 Final Project

## Project Brief
This application will allow users to either randomly encounter 'Pokemon' with different abilities and stats or narrow their encounters by searching for Pokemon types. All Pokemon encountered will have their abilities and stats randomized. The user will only be able to save pokemon to their personal teams if they create an account. If the user decides to register an account, they can choose to save pokemon they have encountered to their personal teams. From the list of all encountered pokemon, users will be able to select and create teams of 1-6 pokemon and save it to their account. Once it is saved, users will have the option to delete the team or update the team with new/previous pokemon they encountered.

## How to Use and Sample Inputs:
When launching the app you will be initially brought to the home page. On the home page, you can click "Enter Tall Grass" to encounter random Pokemon. Each Pokemon you encounter will have a random Ability and Trait (Shiny or regular) assigned to them. Each time you encounter a pokemon, the pokemon is stored in the "Encountered Pokemon" page. You can navigate to this page to see all of the pokemon you have encountered and their respective abilities and traits. There is no way to explicitly search for a pokemon you want to find, but there is a way to narrow down your encounters to specific pokemon types:

** Searching by Type: **
If you navigate from the home page to the "Search By Type" page, you will be able to narrow your encounters by searching various types into the searchbar. For example, you can enter a variety of types such as, but not limited to, "Fire", "Water", "Flying", "Ground", and "Psychic". (For a full list of types please google.) Once a search is entered, if it is a valid search, you will be shown 3 random pokemon of the searched type. The pokemon will again have randomized abilities and traits and can be viewed in your "encountered pokemon" page. Each search entry entered will be stored in the "Search History" page and you may navigate there to view all of the searches that have been made as well as view all of the Pokemon that have been encountered within those searches.

As tests, feel free to enter "water" into the search bar and view the pokemon returned. Now go back and try "flying". Now go back and try "water" again. Now go back again and try searching "pizza." No results will appear. Each time a valid search is entered you will be met with different Pokemon. Now if you navigate to the "Search History" tab, you can view each search you've just made. Clicking on the searches will bring you to a new page where you can see the pokemon you previously encountered using that search. You'll notice that since you searched "water" twice, clicking on that term will show you 6 pokemon and clicking on "pizza" will show you none.

** Filtering Encounters: **
If you navigate to the "All Encounters" page, you will be able to see every single Pokemon you've encountered on the site regardless of how you encountered it. You'll quickly notice after only a few searches and encounters that you'll be into the dozens of pokemon already. To easily filter your encounters, you can enter names or key words you remember from your Pokemon encounters into the search form on this page. Upon submission the form will filter the page and show you Pokemon that in some way match your input.

** Creating Custom Pokemon Teams: **
If you go back to the home page, you'll notice that each time you encounter a pokemon, there is also a link that shows up to create custom Pokemon teams. If you click on the link, you will be brought to a login page, as only registered users can create custom pokemon teams. Alternatively, this also happens if you click on either "Create a team" or "My teams" in the navigation bar. Once at the login page, you can either create an account or login with your Google account if you have one. Once logged in, you will be able to access the Create a team page.

On the Create a team page, you will find a form that prompts you to enter a team name and then choose up to six pokemon to add to that team. Error messages will appear if you select more than 6, no pokemon, or fail to name a team. If your name and choices are valid, you will be redirected to the "My Teams" page where you can view all of the teams you have made and have the option of deleting them. Clicking on them will bring you to a new page showing you all of the pokemon in that team. If you wish to update the team, you will be able to using the Update button on this page. You will be prompted to select the new pokemon you wish to have in the team and will be redirected to the "My Teams" page again after successfully updating your team. If you happen to create a new team that uses the same name as a team you have created previously, this will not be allowed. Please use the "Update" feature instead.

## Additional Pip Modules to Install
There are no additional pip modules to install outside of the ones used in class.

## View Functions/Routes and Templates
http://localhost:5000/ -> index.html

http://localhost:5000/login -> login.html

http://localhost:5000/logout -> index.html

http://localhost:5000/register -> register.html

http://localhost:5000/gCallback -> index.html

http://localhost:5000/type_search -> type_search.html

http://localhost:5000/search_results -> search_results.html

http://localhost:5000/specific_search/<search_term> -> specific_search.html

http://localhost:5000/search_history -> search_history.html

http://localhost:5000/all_encountered -> all_encountered.html

http://localhost:5000/create_team -> create_team.html

http://localhost:5000/teams -> teams.html

http://localhost:5000/single_team/<id_num> -> single_team.html

http://localhost:5000/update/<i> -> update_team.html

http://localhost:5000/delete<team_id> -> teams.html

http://localhost:5000/<invalid route> -> 404.html

http://localhost:5000/<internal error> -> 500.html

## Final Project Requirements Checklist:

- [x] Ensure that your `SI364final.py` file has all the setup (`app.config` values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on `http://localhost:5000` (and the other routes you set up). **Your main file must be called** `SI364final.py`**, but of course you may include other files if you need.**

- [x] A user should be able to load `http://localhost:5000` and see the first page they ought to see on the application.

- [x] Include navigation in `base.html` with links (using `a href` tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, [like this](https://www.dropbox.com/s/hjcls4cfdkqwy84/Screenshot%202018-02-15%2013.26.32.png?dl=0) )

- [x] Ensure that all templates in the application inherit (using template inheritance, with `extends`) from `base.html` and include at least one additional `block`.

- [x] Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).

- [x] Must have data associated with a user and at least 2 routes besides `logout` that can only be seen by logged-in users.

- [x] At least 3 model classes *besides* the `User` class.

- [x] At least one one:many relationship that works properly built between 2 models.

- [x] At least one many:many relationship that works properly built between 2 models.

- [x] Successfully save data to each table.

- [x] Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).

- [x] At least one query of data using an `.all()` method and send the results of that query to a template.

- [x] At least one query of data using a `.filter_by(...` and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).

- [x] At least one helper function that is *not* a `get_or_create` function should be defined and invoked in the application.

- [x] At least two `get_or_create` functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).

- [x] At least one error handler for a 404 error and a corresponding template.

- [x] At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.

- [x] Include at least 4 template `.html` files in addition to the error handling template files.

  - [x] At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.

- [x] At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that *does* accord with other involved sites' Terms of Service, etc).

  - [x] Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source *to the database* (in some way).

- [x] At least one WTForm that sends data with a `GET` request to a *new* page.

- [x] At least one WTForm that sends data with a `POST` request to the *same* page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least one WTForm that sends data with a `POST` request to a *new* page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.

- [x] Include at least one way to *update* items saved in the database in the application (like in HW5).

- [x] Include at least one way to *delete* items saved in the database in the application (also like in HW5).

- [x] Include at least one use of `redirect`.

- [x] Include at least two uses of `url_for`. (HINT: Likely you'll need to use this several times, really.)

- [x] Have at least 5 view functions that are not included with the code we have provided. (But you may have more! *Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.*)


## Additional Requirements for additional points -- an app with extra functionality!

**Note:** Maximum possible % is 102%.

- [x] (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.
- [ ]  (100 points) Create, run, and commit at least one migration.
- [ ] (100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)
- [x]  (100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)
- [x]  (100 points) Implement user sign-in with OAuth (from any other service), and include that you need a *specific-service* account in the README, in the same section as the list of modules that must be installed.
