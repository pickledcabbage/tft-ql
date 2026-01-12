/**
 * QLToolBIS - Best In Slot tool for displaying champion item builds.
 * WRITTEN BY CLAUDE
 */
import {
    Autocomplete,
    Box,
    Button,
    Card,
    Chip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TableSortLabel,
    TextField,
    CircularProgress,
    Typography
} from "@mui/material";
import React, { useEffect, useState, useCallback, useRef } from "react";
import { ENDPOINT } from "../Config";
import axios from "axios";
import { SessionData } from "../SessionData";

/**
 * Champion type from /set_info endpoint.
 * WRITTEN BY CLAUDE
 */
interface Champion {
    apiName: string;
    name: string;
    cost: number;
    traits: string[];
}

/**
 * Item type from /set_info endpoint.
 * WRITTEN BY CLAUDE
 */
interface Item {
    apiName: string;
    name: string;
    composition?: string[];
}

/**
 * Build data from /bis endpoint.
 * WRITTEN BY CLAUDE
 */
interface Build {
    items: string[];
    games: number;
    avg_place: number;
}

type SortField = 'avg_place' | 'games';
type SortDirection = 'asc' | 'desc';

/**
 * Props for QLToolBIS component.
 * WRITTEN BY CLAUDE
 */
interface Props {
    sessionData: SessionData;
    cachedState: any;
    cacheState: (state: any) => void;
    isFocused: boolean;
}

/**
 * Cleans item name by removing commas, periods, and apostrophes.
 * WRITTEN BY CLAUDE
 */
const cleanItemName = (name: string): string => {
    return name.replace(/[,.']/g, '');
};

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column' as const,
        height: '100%',
        padding: '8px',
        gap: '8px'
    },
    searchBar: {
        display: 'flex',
        gap: '8px',
        alignItems: 'center',
        flexWrap: 'wrap' as const
    },
    selectedItems: {
        display: 'flex',
        gap: '4px',
        flexWrap: 'wrap' as const,
        alignItems: 'center'
    },
    tableContainer: {
        flexGrow: 1,
        overflow: 'auto'
    },
    itemCell: {
        fontSize: '12px'
    }
};

/**
 * QLToolBIS component for displaying best in slot item builds.
 * WRITTEN BY CLAUDE
 *
 * @param props - Component props containing sessionData and isFocused
 * @returns React component
 */
export default function QLToolBIS(props: Props) {
    const [champions, setChampions] = useState<Champion[]>([]);
    const [items, setItems] = useState<Item[]>([]);
    const [selectableItems, setSelectableItems] = useState<Item[]>([]);
    const [selectedChamp, setSelectedChamp] = useState<Champion | null>(null);
    const [selectedItems, setSelectedItems] = useState<Item[]>([]);
    const [builds, setBuilds] = useState<Build[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [sortField, setSortField] = useState<SortField>('games');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
    const champInputRef = useRef<HTMLInputElement>(null);

    // Fetch champions and items on mount
    useEffect(() => {
        axios.get(ENDPOINT + '/set_info')
            .then(res => {
                const champs: Champion[] = res.data.champs || [];
                // Sort by cost then name for display
                champs.sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
                setChampions(champs);

                const allItems: Item[] = res.data.items || [];
                setItems(allItems);
                // Include both components and craftable items (items with 2 components)
                const selectable = allItems.filter(item =>
                    !item.composition || item.composition.length === 0 || item.composition.length === 2
                );
                console.log(allItems);
                const uniqueItemMap = new Map();
                selectable.forEach(element => {
                    uniqueItemMap.set(element.name, element);
                });
                const sortedSelectableItems = Array.from(uniqueItemMap.values());
                sortedSelectableItems.sort((a, b) => a.name.localeCompare(b.name));
                setSelectableItems(sortedSelectableItems);
            })
            .catch(e => setError('Error fetching data: ' + e));
    }, []);

    /**
     * Fetches best in slot builds for selected champion.
     * WRITTEN BY CLAUDE
     */
    const fetchBuilds = useCallback(() => {
        if (!selectedChamp) {
            setError('Please select a champion');
            return;
        }

        setLoading(true);
        setError('');

        const itemIds = selectedItems.map(i => i.apiName).join(',');
        const url = itemIds
            ? `${ENDPOINT}/bis?champ_id=${encodeURIComponent(selectedChamp.apiName)}&item_ids=${encodeURIComponent(itemIds)}`
            : `${ENDPOINT}/bis?champ_id=${encodeURIComponent(selectedChamp.apiName)}`;

        axios.get(url)
            .then(res => {
                setBuilds(res.data.builds || []);
            })
            .catch(e => setError('Error fetching builds: ' + e))
            .finally(() => setLoading(false));
    }, [selectedChamp, selectedItems]);

    // Handle CTRL+Enter keyboard shortcut
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'Enter' && props.isFocused) {
                fetchBuilds();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [fetchBuilds]);

    /**
     * Handle CTRL+W keyboard shortcut to focus champion selector.
     * WRITTEN BY CLAUDE
     */
    useEffect(() => {
        if (!props.isFocused) {
            return;
        }
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'w') {
                event.preventDefault();
                champInputRef.current?.focus();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [props.isFocused]);

    /**
     * Handles sort column click.
     * WRITTEN BY CLAUDE
     */
    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection(field === 'avg_place' ? 'asc' : 'desc');
        }
    };

    /**
     * Sorts builds by current sort field and direction.
     * WRITTEN BY CLAUDE
     */
    const sortedBuilds = [...builds].sort((a, b) => {
        const multiplier = sortDirection === 'asc' ? 1 : -1;
        return (a[sortField] - b[sortField]) * multiplier;
    });

    /**
     * Gets item name from API ID.
     * WRITTEN BY CLAUDE
     */
    const getItemName = (apiId: string): string => {
        const item = items.find(i => i.apiName === apiId);
        if (item) {
            return item.name;
        }
        // Fallback: remove TFT prefix
        return apiId.replace(/^TFT\d*_Item_/, '').replace(/^TFT_Item_/, '');
    };

    return (
        <Card sx={{ height: '100%' }}>
            <Box sx={styles.container}>
                <Box sx={styles.searchBar}>
                    <Autocomplete
                        options={champions}
                        value={selectedChamp}
                        onChange={(_e, newValue) => setSelectedChamp(newValue)}
                        getOptionLabel={(option) => `${option.name} (${option.cost})`}
                        isOptionEqualToValue={(option, value) => option.apiName === value.apiName}
                        sx={{ minWidth: 200 }}
                        size="small"
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                inputRef={champInputRef}
                                label="Champion"
                                placeholder="Select champion..."
                            />
                        )}
                    />
                    <Autocomplete
                        options={selectableItems}
                        value={null}
                        onChange={(_e, newValue) => {
                            if (newValue) {
                                setSelectedItems([...selectedItems, newValue]);
                            }
                        }}
                        getOptionLabel={(option) => option.name}
                        filterOptions={(options, { inputValue }) => {
                            console.log(inputValue);
                            const cleaned = cleanItemName(inputValue.toLowerCase());
                            return options.filter(option =>
                                cleanItemName(option.name).toLowerCase().includes(cleaned)
                            );
                        }}
                        sx={{ flexGrow: 1, minWidth: 200 }}
                        size="small"
                        blurOnSelect
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label="Items (optional)"
                                placeholder="Type to search..."
                            />
                        )}
                    />
                    <Button
                        variant="contained"
                        onClick={fetchBuilds}
                        disabled={loading || !selectedChamp}
                    >
                        {loading ? <CircularProgress size={20} /> : 'Search'}
                    </Button>
                </Box>

                {selectedItems.length > 0 && (
                    <Box sx={styles.selectedItems}>
                        {selectedItems.map((item, index) => (
                            <Chip
                                key={`${item.apiName}-${index}`}
                                label={cleanItemName(item.name)}
                                size="small"
                                onDelete={() => {
                                    const newItems = [...selectedItems];
                                    newItems.splice(index, 1);
                                    setSelectedItems(newItems);
                                }}
                            />
                        ))}
                    </Box>
                )}

                {error && (
                    <Typography color="error" variant="body2">{error}</Typography>
                )}

                <TableContainer sx={styles.tableContainer}>
                    <Table size="small" stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Item 1</TableCell>
                                <TableCell>Item 2</TableCell>
                                <TableCell>Item 3</TableCell>
                                <TableCell sortDirection={sortField === 'avg_place' ? sortDirection : false}>
                                    <TableSortLabel
                                        active={sortField === 'avg_place'}
                                        direction={sortField === 'avg_place' ? sortDirection : 'asc'}
                                        onClick={() => handleSort('avg_place')}
                                    >
                                        Avg Place
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell sortDirection={sortField === 'games' ? sortDirection : false}>
                                    <TableSortLabel
                                        active={sortField === 'games'}
                                        direction={sortField === 'games' ? sortDirection : 'desc'}
                                        onClick={() => handleSort('games')}
                                    >
                                        Games
                                    </TableSortLabel>
                                </TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {sortedBuilds.map((build, index) => (
                                <TableRow key={index} hover>
                                    <TableCell sx={styles.itemCell}>
                                        {build.items[0] ? getItemName(build.items[0]) : '-'}
                                    </TableCell>
                                    <TableCell sx={styles.itemCell}>
                                        {build.items[1] ? getItemName(build.items[1]) : '-'}
                                    </TableCell>
                                    <TableCell sx={styles.itemCell}>
                                        {build.items[2] ? getItemName(build.items[2]) : '-'}
                                    </TableCell>
                                    <TableCell>{build.avg_place.toFixed(2)}</TableCell>
                                    <TableCell>{build.games.toLocaleString()}</TableCell>
                                </TableRow>
                            ))}
                            {sortedBuilds.length === 0 && !loading && (
                                <TableRow>
                                    <TableCell colSpan={5} align="center">
                                        <Typography variant="body2" color="textSecondary">
                                            {selectedChamp
                                                ? 'No builds found. Try with different components.'
                                                : 'Select a champion and click Search to view builds.'}
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>
        </Card>
    );
}
