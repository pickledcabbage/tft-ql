// When you create a tool, add an enum for it here.
export enum QLTool {
    QUERY = 'query',
    HOME = 'home',
    STREAMER = 'streamer'
}

// If you want a nice tab name for it, add it here.
export const NAME_MAP = new Map<QLTool, string>([
    [QLTool.QUERY, "Query Tool"],
    [QLTool.HOME, "Home Page"],
    [QLTool.STREAMER, "Session Events"],
]);
