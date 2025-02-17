import { Box, Button, Card, Container, Grid2, IconButton, Typography } from "@mui/material";
import { NAME_MAP, QLTool } from "./QLTool";
import QLToolOpen from "./QLToolOpen";
import QLToolSplit from "./QLToolSplit";
import CloseIcon from '@mui/icons-material/Close';
import HorizontalSplitIcon from '@mui/icons-material/HorizontalSplit';
import VerticalSplitIcon from '@mui/icons-material/VerticalSplit';
import AddIcon from '@mui/icons-material/Add';
import QLToolRaw from "./QLToolRaw";
import { useState } from "react";
import OpenQLToolModal from "./OpenQLToolModal";
import QLToolHome from "./QLToolHome";
import { SessionData } from "./SessionData";
import QLToolStreamer from "./QLToolStreamer";

const styles = {
    container: {
        padding: '0px',
        margin: '0px',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
    },
    card: {
        margin: '4px',
        padding: '4px',
        flexGrow: 1,
        borderRadius: '0px'
    },
    toolbar: {
        '--Grid-borderWidth': '1px',
        borderTop: 'var(--Grid-borderWidth) solid',
        borderLeft: 'var(--Grid-borderWidth) solid',
        borderRight: 'var(--Grid-borderWidth) solid',
        borderBottom: 'var(--Grid-borderWidth) solid',
        borderColor: 'divider',
        justifyContent: 'center',
        alignContent: 'center',
        display: 'flex',
        width: '100%',
    },
    button: {
        padding: '2px',
    },
    icon: {
        height: '12px'
    }
}

// Props that every container gets.
type Props = {
    tool: QLTool,
    cachedState: any,
    containerPath: Array<number>,
    replaceTool: (path: Array<number>, new_tool: QLTool) => void,
    splitNode: (path: Array<number>, direction: 'horizontal' | 'vertical', tool: QLTool) => void,
    closeNode: (path: Array<number>) => void,
    cacheState: (path: Array<number>, state: any) => void,
    sessionData: SessionData,
    setSessionData: (sessionData: SessionData) => void,
};

export default function QLToolContainer(props: Props) {
    const [modalOpen, setModalOpen] = useState<boolean>(false);

    // Fetches a tool and passes it some filtered props. Should probably just pass all of them.
    const getTool = (tool: QLTool) => {
        switch (tool) {
            case QLTool.TEST:
                return (<div>My Test tool!</div>);
            case QLTool.OPEN:
                return (<QLToolOpen replaceSelf={(new_tool: QLTool) => props.replaceTool(props.containerPath, new_tool)} />);
            case QLTool.SPLIT:
                return (<QLToolSplit splitSelf={(new_tool: QLTool, direction: 'vertical' | 'horizontal') => props.splitNode(props.containerPath, direction, new_tool)} />)
            case QLTool.RAW:
                return <QLToolRaw sessionData={props.sessionData} cachedState={props.cachedState} cacheState={(state: any) => props.cacheState(props.containerPath, state)}/>
            case QLTool.HOME:
                return <QLToolHome sessionData={props.sessionData} setSessionData={props.setSessionData}/>
            case QLTool.STREAMER:
                return <QLToolStreamer sessionData={props.sessionData}/>
            default:
                throw new Error('Invalid tool type: ' + tool);
        }
    }

    return (
        <Box sx={styles.container}>
            <OpenQLToolModal isOpen={modalOpen} setModalOpen={setModalOpen} replaceTool={(tool: QLTool) => props.replaceTool(props.containerPath, tool)}/>
            <Grid2 sx={styles.toolbar}>
                <Typography sx={{ flexGrow: 3, display: 'inline-block', marginLeft: '4px'}}>
                    {NAME_MAP.get(props.tool)}
                </Typography>
                <IconButton sx={styles.button} onClick={() => setModalOpen(true)}>
                    <AddIcon sx={styles.icon}/>
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.splitNode(props.containerPath, 'horizontal', QLTool.OPEN)}>
                    <HorizontalSplitIcon sx={styles.icon}/>
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.splitNode(props.containerPath, 'vertical', QLTool.OPEN)}>
                    <VerticalSplitIcon sx={styles.icon}/>
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.closeNode(props.containerPath)}>
                    <CloseIcon sx={styles.icon}/>
                </IconButton>
            </Grid2>
            <Card sx={styles.card}>
                {getTool(props.tool)}
            </Card>

        </Box>
    );
};