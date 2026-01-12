/**
 * QLToolTopComp - Displays top compositions filtered by selected champions.
 * WRITTEN BY CLAUDE
 */
import {
    Autocomplete,
    Box,
    Button,
    Card,
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
import { ENDPOINT } from "./Config";
import axios from "axios";
import { SessionData } from "./SessionData";

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
 * Trait type from /set_info endpoint.
 * WRITTEN BY CLAUDE
 */
interface Trait {
    apiName: string;
    name: string;
}

/**
 * Item type from /set_info endpoint.
 * WRITTEN BY CLAUDE
 */
interface Item {
    apiName: string;
    name: string;
}

/**
 * Composition data from /top_comps endpoint.
 * WRITTEN BY CLAUDE
 */
interface Composition {
    cluster: string;
    units: string[];
    name: ReadonlyArray<{ name: string, type: string}>;
    games: number;
    avg_place: number;
    builds: Record<string, string[]>;
    stars: Record<string, number>;
    traits: [string, number][];
}

type SortField = 'avg_place' | 'games';
type SortDirection = 'asc' | 'desc';

/**
 * Props for QLToolTopComp component.
 * WRITTEN BY CLAUDE
 */
interface Props {
    sessionData: SessionData;
    cachedState: any;
    cacheState: (state: any) => void;
    isFocused: boolean;
}

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
        alignItems: 'center'
    },
    tableContainer: {
        flexGrow: 1,
        overflow: 'auto'
    },
    champCell: {
        fontSize: '12px'
    },
    itemsCell: {
        fontSize: '11px',
        maxWidth: '200px'
    },
    traitsCell: {
        fontSize: '11px',
        maxWidth: '150px'
    }
};

/**
 * QLToolTopComp component for displaying top compositions.
 * WRITTEN BY CLAUDE
 *
 * @param props - Component props containing sessionData
 * @returns React component
 */
export default function QLToolTopComp(props: Props) {
    const [champions, setChampions] = useState<Champion[]>([]);
    const [traits, setTraits] = useState<Trait[]>([]);
    const [items, setItems] = useState<Item[]>([]);
    const [selectedChamps, setSelectedChamps] = useState<Champion[]>([]);
    const [comps, setComps] = useState<Composition[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [sortField, setSortField] = useState<SortField>('games');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
    const inputRef = useRef<HTMLInputElement>(null);

    // Fetch champions, traits, and items on mount
    useEffect(() => {
        axios.get(ENDPOINT + '/set_info')
            .then(res => {
                const champs: Champion[] = res.data.champs || [];
                // Sort by cost then name for display
                champs.sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
                setChampions(champs);
                setTraits(res.data.traits || []);
                setItems(res.data.items || []);
            })
            .catch(e => setError('Error fetching champions: ' + e));
    }, []);

    /**
     * Fetches top compositions based on selected champions.
     * WRITTEN BY CLAUDE
     */
    const fetchComps = useCallback(() => {
        setLoading(true);
        setError('');

        const champIds = selectedChamps.map(c => c.apiName).join(',');
        const url = champIds
            ? `${ENDPOINT}/top_comps?champ_ids=${encodeURIComponent(champIds)}`
            : `${ENDPOINT}/top_comps`;

        axios.get(url)
            .then(res => {
                setComps(res.data.comps || []);
            })
            .catch(e => setError('Error fetching compositions: ' + e))
            .finally(() => setLoading(false));
    }, [selectedChamps]);

    // Handle CTRL+Enter keyboard shortcut
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'Enter' && props.isFocused) {
                fetchComps();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [fetchComps]);

    /**
     * Handle CTRL+W keyboard shortcut to focus search bar.
     * WRITTEN BY CLAUDE
     */
    useEffect(() => {
        if (!props.isFocused) {
            return;
        }
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'w') {
                event.preventDefault();
                inputRef.current?.focus();
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
     * Sorts compositions by current sort field and direction.
     * WRITTEN BY CLAUDE
     */
    const sortedComps = [...comps].sort((a, b) => {
        const multiplier = sortDirection === 'asc' ? 1 : -1;
        return (a[sortField] - b[sortField]) * multiplier;
    });

    /**
     * Gets composition name from name field, converting trait API IDs to readable names.
     * WRITTEN BY CLAUDE
     */
    const getCompName = (comp: Composition): string => {
        // Create a map from trait apiName to readable name
        const traitMap = new Map(traits.map(t => [t.apiName, t.name]));
        const champMap = new Map(champions.map(c => [c.apiName, c.name]));

        return comp.name.map(
            x => {
                if (x.type === 'trait') {
                    return traitMap.get(x.name) || x.type?.replace(/^TFT\d+_/, '') || x.name;
                } else if (x.type === 'unit') {
                    return champMap.get(x.name) || x.type?.replace(/^TFT\d+_/, '') || x.name;
                }
                return x.name
            }
        ).join(" ");
    };

    /**
     * Formats champion list ordered by cost with 3-star indicators.
     * WRITTEN BY CLAUDE
     */
    const formatChampions = (comp: Composition): string => {
        const units = comp.units || [];
        const stars = comp.stars || {};

        // Create a map from apiName to champion data for cost lookup
        const champMap = new Map(champions.map(c => [c.apiName, c]));

        // Sort units by cost
        const sortedUnits = [...units].sort((a, b) => {
            const costA = champMap.get(a)?.cost || 99;
            const costB = champMap.get(b)?.cost || 99;
            return costA - costB;
        });

        return sortedUnits.map(unit => {
            const champData = champMap.get(unit);
            const displayName = champData?.name || unit.replace(/^TFT\d+_/, '');
            const isStar = stars[unit] === 3 || stars[unit] === 1; // stars seems to be a flag
            return isStar ? displayName + '***' : displayName;
        }).join(', ');
    };

    /**
     * Gets top 4 champion items from builds, with newlines between champions.
     * Champion names are rendered in bold. Item API IDs are converted to readable names.
     * WRITTEN BY CLAUDE
     */
    const getTopItems = (comp: Composition): React.ReactNode => {
        const builds = comp.builds || {};
        const itemElements: React.ReactNode[] = [];

        // Create maps for name lookup
        const champMap = new Map(champions.map(c => [c.apiName, c]));
        const itemMap = new Map(items.map(i => [i.apiName, i.name]));

        // Collect items from builds (first few champions)
        const champKeys = Object.keys(builds).slice(0, 4);
        for (let i = 0; i < champKeys.length; i++) {
            const champ = champKeys[i];
            const champItems = builds[champ];
            if (champItems && champItems.length > 0) {
                // Convert champ API ID to readable name
                const champData = champMap.get(champ);
                const champName = champData?.name || champ.replace(/^TFT\d+_/, '');
                // Convert item API IDs to readable names
                const formattedItems = champItems.slice(0, 3).map(itemApiId => {
                    const itemName = itemMap.get(itemApiId);
                    if (itemName) {
                        return itemName;
                    }
                    // Fallback: remove TFT prefix if not found in map
                    return itemApiId.replace(/^TFT\d*_Item_/, '').replace(/^TFT_Item_/, '');
                }).join(', ');

                if (itemElements.length > 0) {
                    itemElements.push(<br key={`br-${i}`} />);
                }
                itemElements.push(
                    <span key={champ}>
                        <strong>{champName}</strong>: {formattedItems}
                    </span>
                );
            }
        }
        return <>{itemElements}</>;
    };

    /**
     * Formats traits with their active levels.
     * WRITTEN BY CLAUDE
     */
    const formatTraits = (comp: Composition): React.ReactNode => {
        const compTraits = comp.traits || [];
        const traitElements: React.ReactNode[] = [];

        for (let i = 0; i < compTraits.length; i++) {
            const [traitApiId, level] = compTraits[i];
            const traitData = traits.find(t => t.apiName === traitApiId);
            const traitName = traitData?.name || traitApiId.replace(/^TFT\d+_/, '');
            traitElements.push(<div key={traitApiId}>{traitName} ({level})</div>);
        }

        return <>{traitElements}</>;
    };

    return (
        <Card sx={{ height: '100%' }}>
            <Box sx={styles.container}>
                <Box sx={styles.searchBar}>
                    <Autocomplete
                        multiple
                        options={champions}
                        value={selectedChamps}
                        onChange={(_e, newValue) => setSelectedChamps(newValue)}
                        getOptionLabel={(option) => `${option.name} (${option.cost})`}
                        isOptionEqualToValue={(option, value) => option.apiName === value.apiName}
                        sx={{ flexGrow: 1 }}
                        size="small"
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                inputRef={inputRef}
                                label="Select Champions"
                                placeholder="Type to search (CTRL + Enter to submit)..."
                            />
                        )}
                    />
                    <Button
                        variant="contained"
                        onClick={fetchComps}
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={20} /> : 'Search'}
                    </Button>
                </Box>

                {error && (
                    <Typography color="error" variant="body2">{error}</Typography>
                )}

                <TableContainer sx={styles.tableContainer}>
                    <Table size="small" stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Champions</TableCell>
                                <TableCell sx={{ minWidth: 250 }}>Items</TableCell>
                                <TableCell>Traits</TableCell>
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
                            {sortedComps.map((comp, index) => (
                                <TableRow key={comp.cluster + '-' + index} hover>
                                    <TableCell>
                                        {getCompName(comp)}
                                        <br />
                                        ({comp.cluster})
                                    </TableCell>
                                    <TableCell sx={styles.champCell}>{formatChampions(comp)}</TableCell>
                                    <TableCell sx={styles.itemsCell}>{getTopItems(comp)}</TableCell>
                                    <TableCell sx={styles.traitsCell}>{formatTraits(comp)}</TableCell>
                                    <TableCell>{comp.avg_place.toFixed(2)}</TableCell>
                                    <TableCell>{comp.games.toLocaleString()}</TableCell>
                                </TableRow>
                            ))}
                            {sortedComps.length === 0 && !loading && (
                                <TableRow>
                                    <TableCell colSpan={6} align="center">
                                        <Typography variant="body2" color="textSecondary">
                                            No compositions found. Try searching with different champions.
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
