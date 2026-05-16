chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({
    text: "OFF", //Extension is off by default when installed
  });
});

chrome.action.onClicked.addListener(async (tab) => {
    // Retrieve the action badge to check if the extension is 'ON' or 'OFF'
    const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
    
    // Next state will always be the opposite
    const nextState = prevState === 'ON' ? 'OFF' : 'ON';
    
    // Set the action badge to the next state
    await chrome.action.setBadgeText({
      tabId: tab.id,
      text: nextState,
    });

    if (nextState === "ON") {
      let currentTabURL;
      try {
        currentTabURL = tab.url;
        currentTabTitle = tab.title;
        if (!currentTabURL) {
          throw new Error("Invalid tab! It might be empty or undefined.");
        }
      } catch (error) {
        console.error("Invalid tab! It might be empty or undefined.", error);
        return;
         }
      console.log(currentTabURL);
      // All the checks go in here
      // Supported sites:
      if (currentTabURL.includes(".civicclerk.com/")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "civicclerk.html" });
        await chrome.action.openPopup(); // opens the popup
        } 
      else if (currentTabURL.includes(".legistar.com")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "legistar.html" });
        await chrome.action.openPopup(); // opens the popup
        } 
      else if (currentTabURL.includes(".granicus.com")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "granicus.html" });
        await chrome.action.openPopup(); // opens the popup
        }
      else if (currentTabURL.includes(".escribemeetings.com")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "escribe.html" });
        await chrome.action.openPopup(); // opens the popup
        }
      else if (currentTabURL.includes(".primegov.com")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "primegov.html" });
        await chrome.action.openPopup(); // opens the popup
        }
      else if (currentTabURL.endsWith("/AgendaCenter")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "agendacenter.html" });
        await chrome.action.openPopup(); // opens the popup
        }
        //NOTE: AgendaCenter is more prevalent than some of those that come before it in this list, 
        // but some pages false-flag agendacenter when they're actually embeds from a previous option, 
        // so we should NOT move this up the list.
      else if (currentTabURL.includes(".iqm2.com")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "iqm2.html" });
        await chrome.action.openPopup(); // opens the popup
        }
      else if (currentTabURL.includes("onbase") || currentTabTitle.includes("OnBase Agenda Online")){
        await chrome.action.setPopup({ tabId: tab.id, popup: "onbase.html" });
        await chrome.action.openPopup();
        }
      //else if (source includes "Aha change 20170911"): municode 
        // Comment originating from a dependency but their code uses such clear language 
        // that nothing else feels specific to them
      //else if (condition TKTK): eboard - seemingly not yet in use?
      //else if (condition TKTK): laserfiche - unfinished WIP   
      //else if (there's an Archive link): ask the user to click it and run this again
      //actual else: Assume custom scraper; for now I'm using the placeholder because I don't want to fill the issue tracker with junk data
        else {
          await chrome.action.setPopup({ tabId: tab.id, popup: "hello.html" });
          await chrome.action.openPopup(); // opens the popup
        }
      };
});