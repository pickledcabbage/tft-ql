import { Box, } from "@mui/material";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import 'react-reflex/styles.css';
import QLToolbar from "./QLToolbar";
import QLToolContainer from "./QLToolContainer";
import { QLTool } from "./QLTool";
import { useState } from "react";
import path from "path";
import { ConstructionOutlined } from "@mui/icons-material";
import { SessionData } from "./SessionData";


const styles = {
    background: {
        width: '100vw',
        height: '100vh',
        backgroundColor: 'lightgray'
    }
}

type QLToolNode = {
    type: 'tool' | 'vertical' | 'horizontal',
    tool?: QLTool,
    children: Array<QLToolNode>,
}

export default function Workspace() {
    const [state, setState] = useState<QLToolNode>({
        type: 'tool',
        tool: QLTool.HOME,
        children: []
    } as QLToolNode);
    const [toolStateCache, setToolStateCache] = useState<Map<string, any>>(new Map());
    const [sessionData, setSessionData] = useState<SessionData>({id: '', connected: false, joinCode: ''});

    // Helpers for finding nodes.
    const findNode = (node: QLToolNode, path: Array<number>): QLToolNode | null => {
        if (path.length == 0) {
            return node;
        }
        const loc = path[0];
        if (loc >= node.children.length) return null;
        const next_node = node.children[loc];
        return findNode(next_node, path.slice(1));
    }

    // Replaces tool at location. Used with open tool.
    const replaceTool = (path: Array<number>, new_tool: QLTool) => {
        const new_state = structuredClone(state);
        const node = findNode(new_state, path);
        if (node != null && node.type == 'tool') {
            node.tool = new_tool;
        }
        setState(new_state);
    }

    // Splits a node vertically or horizontally.
    const splitNode = (path: Array<number>, direction: 'horizontal' | 'vertical', tool: QLTool = QLTool.OPEN) => {
        // The case where there is only one node.
        if (path.length == 0) {
            const new_state = {
                type: direction,
                children: [
                    state,
                    {
                        type: 'tool',
                        tool,
                        children: []
                    }
                ]
            } as QLToolNode;
            setState(new_state);
            return;
        }
        // Otherwise there will always be a parent node.
        const new_state = structuredClone(state);
        const parentNode = findNode(new_state, path.slice(0, -1));
        const loc = path[path.length - 1];
        if (parentNode == null || loc >= parentNode.children.length) {
            return;
        }
        const nodeToSplit = parentNode.children[loc];
        if (parentNode.type == direction) {
            // If same direction then interleave the new node.
            // 0 1 2 if loc = 1, then slice(0, loc) + new_node + slice(loc+1);
            const front = parentNode.children.slice(0, loc+1);
            const end = parentNode.children.slice(loc+1);
            const new_node = {
                type: 'tool',
                tool,
                children: [],
            } as QLToolNode;
            parentNode.children = front.concat([new_node], end);
            setState(new_state);
            return;
        }
        // Otherwise split the node.
        parentNode.children[loc] = {
            type: direction,
            children: [
                nodeToSplit,
                {
                    type: 'tool',
                    tool,
                    children: [],
                }
            ]
        };
        setState(new_state);
    }

    // Closes a node.
    const closeNode = (path: Array<number>) => {
        const new_state = structuredClone(state);
        const closeNodeRec = (node: QLToolNode, path: Array<number>) => {
            if (path.length == 0) return;
            const loc = path[0];
            if (loc >= node.children.length) {
                return;
            }
            closeNodeRec(node.children[loc], path.slice(1));
            if (path.length == 1 || node.children[loc].children.length == 0) {
                node.children = node.children.slice(0, loc).concat(node.children.slice(loc+1));
            }

        }
        closeNodeRec(new_state, path);
        // If we deleted up to the last node.
        if (path.length == 0 || new_state.children.length == 0) {
            setState({
                type: 'tool',
                tool: QLTool.OPEN,
                children: [],
            } as QLToolNode);
        } else {
            setState(new_state);
        }
    }

    // Updates value in state cache for tool.
    const cacheState = (path: Array<number>, state: any) => {
        const newCache = structuredClone(toolStateCache);
        newCache.set(path.join(':'), state);
        setToolStateCache(newCache);
    }

    // Generates the containers.
    const createReflexContainers = (node?: QLToolNode, path?: Array<number>) => {
        if (node == null || path == null) return (<div />);
        if (node.type == 'tool' && node.tool != null) {
            return (<QLToolContainer sessionData={sessionData} setSessionData={setSessionData} cachedState={toolStateCache.get(path.join(':'))} cacheState={cacheState} tool={node.tool} containerPath={path} replaceTool={replaceTool} splitNode={splitNode} closeNode={closeNode} />)
        } else if ((node.type == 'vertical' || node.type == 'horizontal') && node.children != null) {
            const elements = node.children.map((value, index) => (
                <ReflexElement className={index.toString()}>
                    {createReflexContainers(value, path.concat([index]))}
                </ReflexElement>
            ));
            let interleaved: Array<JSX.Element> = [];
            for (let i = 0; i < elements.length; ++i) {
                if (i != 0) interleaved.push(<ReflexSplitter/>);
                interleaved.push(elements[i]);
            }
            return (
                <ReflexContainer orientation={node.type}>
                    {interleaved}
                </ReflexContainer>
            )
        }
    }

    return (
        <Box sx={styles.background}>
            {/* <QLToolbar /> */}
            {createReflexContainers(state, [])}
        </Box>
    );
}