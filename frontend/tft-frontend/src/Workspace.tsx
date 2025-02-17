import { Box, } from "@mui/material";
import { ReflexContainer, ReflexElement, ReflexSplitter } from "react-reflex";
import 'react-reflex/styles.css';
import QLToolbar from "./QLToolbar";
import QLToolContainer from "./QLToolContainer";
import { QLTool } from "./QLTool";


const styles = {
    card: {
        margin: '8px',
        padding: '8px',
    },
    background: {
        width: '100vw',
        height: '100vh',
        backgroundColor: 'lightgray'
    }
}

type QLToolNode = {
    type: 'tool' | 'vertical' | 'horizontal',
    tool?: QLTool,
    children?: Map<string, QLToolNode>,
}

export default function Workspace() {
    const state = {
        type: 'horizontal',
        children: new Map(
            [
                ['0', { type: 'tool', tool: QLTool.OPEN }],
                ['1', { type: 'tool', tool: QLTool.TEST }],
            ]
        )
    } as QLToolNode;

    const createReflexContainers = (node?: QLToolNode, path?: Array<string>) => {
        if (node == null || path == null) return (<div />);
        if (node.type == 'tool' && node.tool != null) {
            return (<QLToolContainer tool={node.tool} containerPath={path} />)
        } else if ((node.type == 'vertical' || node.type == 'horizontal') && node.children != null) {
            const elements = Array.from(node?.children?.entries() ?? []).map(([key, value]) => (
                <ReflexElement className={key}>
                    {createReflexContainers(value, path.concat(key))}
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
            <QLToolbar />
            {createReflexContainers(state, [])}
        </Box>
    );
}