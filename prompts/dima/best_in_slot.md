We will be creating a tool for the UI called "Best In Slot" or "bis" that is UI version of terminal interpreter command in tft/commands/best_in_slot.py.

A great example of a previously written tool is QLToolTopComp.tsx.

This tool should do the following:
1. Have a single selector for champions that lets you type and in will autocomplete the champion name (similar to QLToolTopComp's search bar, but in this case we can only select one champion). The search should by name not by API ID.
2. Have a multiselector where you can select items that you currently have. Similar to the QLToolTopComp's multiselector with autocomplete typing.
3. A submit button to submit the selected data to the server. You should be able to press CTRL + Enter to submit the button in the tool.
4. When you press CTRL + W it should focus on the champion selector, letting you search for a new champion.
5. A new endpoint should be created in tft/interpreter/server.py which receives the submitted data (the data should all be API IDs) and it should return a list of the top items with each item group having average place and number of games. It must include items that were passed to the endpoint or can build from the passed components. The function `get_recipes()` from tft/queries/items.py returns the recipe for each item that can be built. It is possible there is less than 3 completed items.
6. The data should be rendered in the UI tool in the form of a table. With columns: Item 1, Item 2, Item 3, Average Place, Games Played. The table should be sortable by average place and games played.