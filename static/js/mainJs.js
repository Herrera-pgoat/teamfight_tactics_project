//Getting the load more button
let loadMoreBtn = document.getElementById('load_more');

//we are gonna use this variable to make sure we can't click the button multiple times.
let isLoadingGames = false;

function loadMoreGamesFunc(){
  if (isLoadingGames){
    return false;
  }
  else{

    //at the end we make isLoadingGames to true
    //not sure this really works but whatever. 
    isLoadingGames=true;
  }

  //what happens is that when you push the button this function will activate
  //This will get the name of the person we are following
  //then it will search the api for more games of that person name
  //then we will count how many games we already have and load three more
  //if there are no more games then it will kill the button and say no more games found.
}

//when the user clicks the button we load more games.
loadMoreBtn.addEventListener('onclick',loadMoreGamesFunc);
