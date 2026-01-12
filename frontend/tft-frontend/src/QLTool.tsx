// When you create a tool, add an enum for it here.
export enum QLTool {
    QUERY = 'query',
    HOME = 'home',
    STREAMER = 'streamer',
    ALIAS_ADDER = 'alias_adder',
    TOP_COMP = 'top_comp',
    BIS = 'bis'
}

// If you want a nice tab name for it, add it here.
export const NAME_MAP = new Map<QLTool, string>([
    [QLTool.QUERY, "Query Tool"],
    [QLTool.HOME, "Home Page"],
    [QLTool.STREAMER, "Session Events"],
    [QLTool.ALIAS_ADDER, "Alias Adder"],
    [QLTool.TOP_COMP, "Top Comps"],
    [QLTool.BIS, "Best In Slot"],
]);
