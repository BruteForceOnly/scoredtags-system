// currently made to work for Tag Library specifically, but should be generalizable?
function getSearchParam(paramName) {
    let parameters = new URLSearchParams(window.location.search);
    if (parameters.get(paramName) !== null) {
        return parameters.get(paramName);
    }
    return "";
}

// additional content functionality
function hideAdditionalContent() {
    let additionalContentElmt = document.getElementById("additional-content-window");
    additionalContentElmt.style.display = "none";
    let showACButton = document.getElementById("additional-content-widgets");
    showACButton.style.display = "flex";
}

function showAdditionalContent() {
    let additionalContentElmt = document.getElementById("additional-content-window");
    additionalContentElmt.style.display = "flex";
    let showACButton = document.getElementById("additional-content-widgets");
    showACButton.style.display = "none";
}

// add new item button (used on: library page, info page)
//function addNewItemButtonClicked(addButtonId, inputUIId) {
function addNewItemButtonClicked(eltToHideId, eltToShowId) {
    /*let addButton = document.getElementById(addButtonId);
    addButton.style.display = "none";
    let inputUI = document.getElementById(inputUIId);
    inputUI.style.display = "flex";*/
    let eltToHide = document.getElementById(eltToHideId);
    eltToHide.style.display = "none";
    let eltToShow = document.getElementById(eltToShowId);
    eltToShow.style.display = "flex";
}

//function newItemCancelButtonClicked(addButtonId, inputUIId) {
function newItemCancelButtonClicked(eltToShowId, eltToHideId) {
    /*let inputUI = document.getElementById(inputUIId);
    inputUI.style.display = "none";
    let addButton = document.getElementById(addButtonId);
    addButton.style.display = "initial";*/
    let eltToHide = document.getElementById(eltToHideId);
    eltToHide.style.display = "none";
    let eltToShow = document.getElementById(eltToShowId);
    eltToShow.style.display = "initial";
}

function relatedUIShowHide(eltToShowId, shownDisplayType, eltToHideId) {
    let eltToHide = document.getElementById(eltToHideId);
    eltToHide.style.display = "none";
    let eltToShow = document.getElementById(eltToShowId);
    eltToShow.style.display = shownDisplayType;
}


// search, then select/add (new) item (aka search-select)
function handleSearchSelectResultClicked(thisElt, eltsUID, resultPk) {
    let inputElt = document.getElementById("new-item-name-input-" + eltsUID);
    let hiddenInputElt = document.getElementById("selected-item-pk-input-" + eltsUID);
    let resultName = thisElt.textContent.trim();
    // clear any previous input values/placeholders
    inputElt.value = "";
    //inputElt.placeholder = "";
    //hiddenInputElt.value = "";
    // set input values
    inputElt.placeholder = resultName;
    hiddenInputElt.value = resultPk;
}

function handleSearchSelectCreateNewItemClicked(eltsUID) {
    let inputElt = document.getElementById("new-item-name-input-" + eltsUID);
    let hiddenInputElt = document.getElementById("selected-item-pk-input-" + eltsUID);
    let itemName = document.getElementById("search-select-input-" + eltsUID).value;
    // clear any previous input values/placeholders
    //inputElt.value = "";
    inputElt.placeholder = "";
    hiddenInputElt.value = "";
    // set input values
    inputElt.value = itemName;
}

function getLockedInSearchSelectItemName(newItemNameInputId){
    let newItemNameInputElt = document.getElementById(newItemNameInputId);
    let lockedInItemName = "";
    if(newItemNameInputElt.placeholder != ""){
        lockedInItemName = newItemNameInputElt.placeholder;
    } else if(newItemNameInputElt.value != ""){
        lockedInItemName = newItemNameInputElt.value;
    }
    return lockedInItemName;
}


// used in shareddata-type ui stuff
function showAllElementsWithClass(classStr, displayValue) {
    let selectedElts = document.getElementsByClassName(classStr);
    for(let k=0; k<selectedElts.length; k++){
        selectedElts[k].style.display = displayValue;
    }
}

function hideAllElementsWithClass(classStr) {
    let selectedElts = document.getElementsByClassName(classStr);
    for(let k=0; k<selectedElts.length; k++){
        selectedElts[k].style.display = "none";
    }
}


// error handling
function setErrorElementContents(elt, errorMsg) {
    elt.innerText = "";
    let newErrorElement = document.createElement("p");
    newErrorElement.className = "error-message";
    newErrorElement.innerText = "Error: " + errorMsg;
    elt.appendChild(newErrorElement);
}

function hideErrorElement(elt_id) {
    let elt = document.getElementById(elt_id);
    elt.style.display = "none";
}

// is there a point in having the above, "hideErrorElement"??
// should really swap out all the instances of its use
function hideElement(elt_id) {
    let elt = document.getElementById(elt_id);
    elt.style.display = "none";
}

function showElement(elt_id) {
    let elt = document.getElementById(elt_id);
    elt.style.display = "initial";
}

function displayErrorElement(evt) {
    let error_elt = null;
    let elmt = evt.detail.elt;
    // handle errors from different elements
    if(elmt.id == "library-searchbar" 
        || elmt.id == "library-sortby-name" || elmt.id == "library-sortby-date"
    ) {
        error_elt = document.getElementById("library-search-sort-errors");
        setErrorElementContents(error_elt, "Failed to search/sort the items");
    } 
    else if(
        elmt.classList.contains("library-table-page-link") || elmt.id == "go-to-input" 
        || elmt.id == "library-next-page-button" || elmt.id == "library-prev-page-button"
    ) {
        error_elt = document.getElementById("library-paging-errors");
        setErrorElementContents(error_elt, "Could not go to page");
    }
    else if( (elmt.id).includes("add-new-item-confirm") ) {
        let uid = elmt.id.substring( ((elmt.id).lastIndexOf('-') + 1), elmt.id.length );
        pushMessageListItem("message-list-" + uid, "error", "Error");
    }
    else if( (elmt.id).includes("edit-date-confirm") ) {
        if(elmt.getAttribute("hx-target") == "#rdate-data") {
            pushMessageListItem("message-list-rdate", "error", "Error");
        } else if(elmt.getAttribute("hx-target") == "#ludate-data") {
            pushMessageListItem("message-list-ludate", "error", "Error");
        }
    }
    else if(elmt.id == "edit-sdtype-confirm") {
       pushMessageListItem("message-list-marked-as-type", "error", "Error");
    }
    else if(elmt.id == "select-overall-user-score-confirm"){
        pushMessageListItem("message-list-oscore", "error", "Error");
    }
    // display the error element
    if(error_elt != null){
        error_elt.style.display = "block";
    }
}


//message-list (should you replace the older method of success/error messages?)
function clearMessageList(listEltId) {
    let msgListElt = document.getElementById(listEltId);
    msgListElt.replaceChildren();
}

function pushMessageListItem(listEltId, msgType, msg) {
    let msgListElt = document.getElementById(listEltId);
    let df = document.createDocumentFragment();
    // create and define all elements
    let s = document.createElement("span");
    s.className = "message-list-item";
    let p = document.createElement("p");
    if(msgType == "error") {
        p.className = "error-message";
        p.innerText = "||\u2BBE|| " + msg + " ";
    } else if(msgType == "success") {
        p.className = "success-message";
        p.innerText = "||\u2611|| " + msg + " ";
    }
    let b = document.createElement("button");
    b.className = "message-list-item-button";
    b.onclick = function(){ popMessageListItem(this) };
    b.innerText = "\u2715"
    // arrange elements into proper structure and add them
    df.appendChild(s);
    s.appendChild(p);
    p.appendChild(b);
    msgListElt.appendChild(df);
}

function popMessageListItem(closeButton) {
    if(closeButton.parentElement.parentElement.className == "message-list-item"){
        closeButton.parentElement.parentElement.remove();
    }
}


// csrf token
function get_csrf_token() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// editable content overlay
function generateEditableUI(elt) {
    let UI = document.createElement("div");
    UI.className = "editable-ui";
    elt.appendChild(UI);
    let editButton = document.createElement("button");
    editButton.innerText = "edit"
    UI.appendChild(editButton);
}

function showTableRow(elt_id) {
    let tr_elt = document.getElementById(elt_id);
    tr_elt.style.display = "table-row";
}

function hideTableRow(elt_id) {
    let tr_elt = document.getElementById(elt_id);
    tr_elt.style.display = "none";
}

// tabs
function setActiveTab(thisElement, tabID, tabGroupID, extraEltToHideID="", extraEltToShowID="") {
    // select the tab group
    let tabGroup = document.getElementById(tabGroupID);
    // deactivate previous selected tabs
    let tabButtons = tabGroup.getElementsByClassName("tab-button");
    for(let k = 0; k < tabButtons.length; k++) {
        tabButtons[k].classList.remove("active-tab");
    }
    // hide all tab content
    let allTabs = tabGroup.getElementsByClassName("tab-content");
    for(let k = 0; k < allTabs.length; k++) {
        allTabs[k].classList.remove("active-tab");
    }
    // hide extra element that needs to be hidden
    if(extraEltToHideID != "") {
        document.getElementById(extraEltToHideID).style.display = "none";
    }
    // show active tab
    let activeTab = document.getElementById(tabID);
    activeTab.classList.add("active-tab");
    // make element active
    thisElement.classList.add("active-tab");
    // show extra element that needs to be shown
    if(extraEltToShowID != "") {
        document.getElementById(extraEltToShowID).style.display = "block";
    }
}

// top navbar search
function setTopNavSearchResults(selectElt) {
    let selectedResultsType = selectElt.options[selectElt.selectedIndex].value;
    let topNavSearchElt = document.getElementById("search-select-input-0");
    topNavSearchElt.setAttribute("hx-vals", `{"searchtype": "${selectedResultsType}"}`);
}

function getTopNavSearchInputValue() {
    let topNavSearchElt = document.getElementById("search-select-input-0");
    return topNavSearchElt.value;
}

function getCurrentlySelectedSearchType() {
    let selectElt = document.getElementById("searchbar-choice");
    return selectElt.options[selectElt.selectedIndex].value;
}

// tags list search, copied from top navbar search, CONSIDER MERGING THEM TO USE THE SAME
function getSearchInputValue(inputEltId) {
    let inputElt = document.getElementById(inputEltId);
    return inputElt.value;
}

function getSearchSelectedOptionValue(selectEltId) {
    let selectElt = document.getElementById(selectEltId);
    return selectElt.options[selectElt.selectedIndex].value;
}

// copied from above...should probably replace those with this function instead
function getSelectedOptionValue(selectEltId) {
    let selectElt = document.getElementById(selectEltId);
    return selectElt.options[selectElt.selectedIndex].value;
}


// drag and drop (project series ordering)
function dragstartHandler(ev) {
    // clear visual indicators
    ev.target.style.backgroundColor = "transparent";
    if (ev.target.previousElementSibling != null){
        ev.target.previousElementSibling.style.backgroundColor = "transparent";
    }
    if (ev.target.nextElementSibling != null) {
        ev.target.nextElementSibling.style.backgroundColor = "transparent";
    }
    // Add the target element's id to the data transfer object
    ev.dataTransfer.setData("text/html", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
}

function dragoverHandler(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "move";
}

function dragenterHandler(ev) {
    ev.target.parentNode.style.backgroundColor = "lightgreen";
}

function dragleaveHandler(ev) {
    ev.target.parentNode.style.backgroundColor = "transparent";
}

function dropHandler(ev, el) {
    ev.preventDefault();
    // Get the id of the target and add the moved element to the target's DOM
    const data = ev.dataTransfer.getData("text/html");
    if (el.getAttribute("data-rel-pos") == "before") {
        el.parentNode.insertBefore(document.getElementById(data), el.nextSibling);
    }else if (el.getAttribute("data-rel-pos") == "after") {
        el.parentNode.insertBefore(document.getElementById(data), el);
    }
    // visual indicators
    let draggableElt = document.getElementById("draggable-series-project");
    draggableElt.style.backgroundColor = "lightgreen";
    let adjacentElt = document.getElementById("series-entry-" + el.getAttribute("data-rel-pk"));
    adjacentElt.style.backgroundColor = "lightgreen";
    // unmark previously selected element(s) (though it should really only be 1)
    previouslySelectedElts = document.getElementsByClassName("selected-series-order-target");
    for(let k=0; k<previouslySelectedElts.length; k++){
        previouslySelectedElts[k].classList.remove("selected-series-order-target");
    }
    // mark the element containing the data for the future related htmx request
    el.classList.add("selected-series-order-target");
}

function getSelectedSeriesOrderTargetData(dataType) {
    targetElt = document.querySelector(".selected-series-order-target");
    if(targetElt == null) {
        return ""
    }
    if(dataType == "entry") {
        return targetElt.getAttribute("data-rel-pk");
    }else if(dataType == "position"){
        return targetElt.getAttribute("data-rel-pos");
    }else{
        return "";
    }
}


// altnames
function showHideMoreAltnames() {
    let showHideButtonElt = document.getElementById("show-hide-more-altnames");
    let altnamesDiv = document.getElementById("swappable-altnames-list-data");
    if(showHideButtonElt.innerText == "show more") {
        altnamesDiv.style.webkitLineClamp = "initial";
        showHideButtonElt.innerText = "hide more";
    } else if(showHideButtonElt.innerText == "hide more") {
        altnamesDiv.style.webkitLineClamp = 2;
        showHideButtonElt.innerText = "show more"
    }
}


// initialization stuff to do when page loads
// for handling page errors
document.addEventListener(
    "htmx:error", 
    (evt) => { displayErrorElement(evt) }
);
// for editable pages
let editables = document.querySelectorAll(".editable-container");
editables.forEach( element => {
    generateEditableUI(element);
});



