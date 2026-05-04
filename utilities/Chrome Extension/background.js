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
      if (condition): agendacenter
      elif (condition): civicclerk
      elif (URL contains *.legistar.com): legistar
      elif (condition): granicus
      elif (condition): escribe
      elif (condition): primegov
      elif (condition): iqm2
      elif (condition): onbase
      elif (condition): municode
      elif (condition): eboard - seemingly not yet in use?
      elif (condition): laserfiche - unfinished WIP   
      elif (there's an Archive link): ask the user to click it and run this again
      else: Assume custom scraper */
      };
     else if (nextState === "OFF") {
      // If we end up using any temp files or similar, we should delete those
      // Maybe there will be cleanup to go in here, but probably not
      };
});