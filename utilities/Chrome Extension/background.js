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
      // All the checks go in here
      /* Supported sites:
      if (URL contains *.civicclerk.com/): civicclerk
      elif (URL contains *.legistar.com): legistar
      elif (URL contains *.granicus.com): granicus
      elif (URL contains *.escribemeetings.com): escribe
      elif (URL contains *.primegov.com): primegov
      elif (primary page URL ends in /agendacenter): agendacenter 
        //NOTE: AgendaCenter is more prevalent than some of those that come before it in this list, 
        // but some pages false-flag agendacenter when they're actually embeds from a previous option, 
        // so we should NOT move this up the list.
      elif (URL contains *.iqm2.com): iqm2
      elif (URL contains *onbase* OR [other conditions TKTK]): onbase
      elif (course includes "Aha change 20170911"): municode 
        // Comment originating from a dependency but their code uses such clear language 
        // that nothing else feels specific to them
      elif (condition TKTK): eboard - seemingly not yet in use?
      elif (condition TKTK): laserfiche - unfinished WIP   
      elif (there's an Archive link): ask the user to click it and run this again
      else: Assume custom scraper */
      };
     else if (nextState === "OFF") {
      // If we end up using any temp files or similar, we should delete those
      // Maybe there will be cleanup to go in here, but probably not
      };
});