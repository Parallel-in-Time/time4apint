('use strict');

import { init } from './init.js';
import { elements } from './elements.js';
import { State } from './state.js';
import { Connection } from './connection.js';

// Create the global state
const state = new State(elements);

// Create a connection handler
const connection = new Connection();

// Initialize all the elements with the state
init(elements, state, connection);
