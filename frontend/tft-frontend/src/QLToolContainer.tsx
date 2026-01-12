import { Box, Card, Container, Grid2, IconButton, Typography } from "@mui/material";
import { NAME_MAP, QLTool } from "./QLTool";
import CloseIcon from '@mui/icons-material/Close';
import HorizontalSplitIcon from '@mui/icons-material/HorizontalSplit';
import VerticalSplitIcon from '@mui/icons-material/VerticalSplit';
import SearchIcon from '@mui/icons-material/Search';
import QLToolRaw from "./tools/QLToolRaw";
import React, { useEffect, useRef, useState } from "react";
import OpenQLToolModal from "./OpenQLToolModal";
import QLToolHome from "./tools/QLToolHome";
import { SessionData } from "./SessionData";
import QLToolStreamer from "./tools/QLToolStreamer";
import QLToolAliasAdder from "./tools/QLToolAliasAdder";
import QLToolTopComp from "./tools/QLToolTopComp";
import QLToolBIS from "./tools/QLToolBIS";
import { useFocusManager, useFocusWithin } from 'react-aria';

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
    isFocused: boolean,
    requestFocus: (path: Array<number>) => void,
    moveFocus: (path: Array<number>, direction: 'left' | 'right' | 'up' | 'down') => void,
};

export default function QLToolContainer(props: Props) {
    const [modalOpen, setModalOpen] = useState<boolean>(false);

    // Checks to see if we are focused within this container.
    let { focusWithinProps } = useFocusWithin({
        onFocusWithin: (e) => {
            props.requestFocus(props.containerPath);
        },
        onFocusWithinChange: (isFocusWithin) => {
            if (isFocusWithin) {
                props.requestFocus(props.containerPath);
            }
        }
    });


    // Keyboard commands.
    const handleKeyDown = (event: any) => {
        if (!props.isFocused) return;
        if (event.ctrlKey && event.key === 'q') {
            setModalOpen(true);
        }
        if (event.ctrlKey) {
            if (event.key === 'ArrowUp') {
                props.moveFocus(props.containerPath, 'up');
            }
            if (event.key === 'ArrowDown') {
                props.moveFocus(props.containerPath, 'down');
            }
            if (event.key === 'ArrowLeft') {
                props.moveFocus(props.containerPath, 'left');
            }
            if (event.key === 'ArrowRight') {
                props.moveFocus(props.containerPath, 'right');
            }
        }
    };
    useEffect(() => {
        if (!props.isFocused) {
            return;
        }
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('keydown', handleKeyDown); // Clean up listener
        };
    }, [props.isFocused]);



    // Fetches a tool and passes it some filtered props. Should probably just pass all of them.
    const getTool = (tool: QLTool) => {
        switch (tool) {
            case QLTool.QUERY:
                return <QLToolRaw sessionData={props.sessionData} cachedState={props.cachedState} cacheState={(state: any) => props.cacheState(props.containerPath, state)} />
            case QLTool.HOME:
                return <QLToolHome sessionData={props.sessionData} setSessionData={props.setSessionData} />
            case QLTool.STREAMER:
                return <QLToolStreamer sessionData={props.sessionData} />
            case QLTool.ALIAS_ADDER:
                return <QLToolAliasAdder />
            case QLTool.TOP_COMP:
                return <QLToolTopComp sessionData={props.sessionData} cachedState={props.cachedState} cacheState={(state: any) => props.cacheState(props.containerPath, state)} isFocused={props.isFocused} />
            case QLTool.BIS:
                return <QLToolBIS sessionData={props.sessionData} cachedState={props.cachedState} cacheState={(state: any) => props.cacheState(props.containerPath, state)} isFocused={props.isFocused} />
            default:
                throw new Error('Invalid tool type: ' + tool);
        }
    }

    return (
        <Box sx={styles.container} {...focusWithinProps}>
            <OpenQLToolModal isOpen={modalOpen} setModalOpen={setModalOpen} replaceTool={(tool: QLTool) => { props.replaceTool(props.containerPath, tool); props.requestFocus(props.containerPath); }} />
            <Grid2 sx={styles.toolbar}>
                <Typography sx={{ flexGrow: 3, display: 'inline-block', marginLeft: '4px' }}>
                    {(NAME_MAP.get(props.tool) ?? 'Unknown') + (props.isFocused ? '*' : '')}
                </Typography>
                <IconButton sx={styles.button} onClick={() => setModalOpen(true)}>
                    <SearchIcon sx={styles.icon} />
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.splitNode(props.containerPath, 'horizontal', QLTool.QUERY)}>
                    <HorizontalSplitIcon sx={styles.icon} />
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.splitNode(props.containerPath, 'vertical', QLTool.QUERY)}>
                    <VerticalSplitIcon sx={styles.icon} />
                </IconButton>
                <IconButton sx={styles.button} onClick={() => props.closeNode(props.containerPath)}>
                    <CloseIcon sx={styles.icon} />
                </IconButton>
            </Grid2>
            <Card sx={styles.card}>
                {getTool(props.tool)}
            </Card>
        </Box>
    );
};