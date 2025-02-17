import { Card } from "@mui/material";
import { QLTool } from "./QLTool";
import QLToolOpen from "./QLToolOpen";

const styles = {
    card: {
        padding: '8px',
        margin: '8px',
        height: '100%',
        width: '100%'
    }
}

type Props = {
    tool: QLTool
    containerPath: Array<string>
    // Add actions here.
};

const getTool = (tool: QLTool) => {
    switch(tool) {
        case QLTool.TEST:
            return (<div style={{height: '60vh'}}>My Test tool!</div>);
        case QLTool.OPEN:
            return (<QLToolOpen/>);
        default:
            throw new Error('Invalid tool type: ' + tool);
    }
}

export default function QLToolContainer(props: Props) {
    return (
        <Card sx={styles.card}>
            {getTool(props.tool)}
        </Card>
    );
};