// When you create a tool, add an enum for it here.
export enum QLTool {
    TEST = 'test',
    OPEN = 'open',
    SPLIT = 'split',
    RAW = 'raw',
    HOME = 'home',
    STREAMER = 'streamer'
}

// If you want a nice tab name for it, add it here.
export const NAME_MAP = new Map<QLTool, string>([
    [QLTool.TEST, "Test Tool"],
    [QLTool.OPEN, "Open Tool"],
    [QLTool.SPLIT, "Split Tool"],
    [QLTool.RAW, "Query Tool"],
    [QLTool.HOME, "Home Page"],
    [QLTool.STREAMER, "Session Events"],
]);
