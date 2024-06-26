import py_trees
from Controllers.behaviors import *
from Model.agent import Agent
from Model.feeding_site import Site

def build_bt(agent):
    # Rest subtree
    rest_root = py_trees.decorators.Repeat("Graze_Root",
                                           py_trees.composites.Sequence("Graze", False, children=[AtSite("AtSite", agent), 
                                                                        HaveGroupNeighbors("Group", agent),
                                                                        #py_trees.decorators.Inverter("Inverter", IsBored("Timer", agent)),
                                                                        Graze("Rest", agent)]), AGENT_BORED_THRESHOLD)

    # GoToSite subtree
    goToSite_subtree = py_trees.composites.Sequence("GoToSite_Actions", False, [HaveNeighbors("Neighbors", agent),
                                                                                GoToSite("GoToSite", agent),
                                                                                Flock("GoToSite_Flock", agent, attr_factor=0.5, diff_factor=0.5)])
    goToSite_root = py_trees.composites.Sequence("GoToSite_Root", False, [SiteSelected("SiteSelected", agent),
                                                                        goToSite_subtree])

    # Explore subtree
    flock_root = py_trees.composites.Sequence("Flock Root", False, [#py_trees.decorators.Inverter("Inverter", IsBored("Bored_Explore", agent)),
                                                                        QueryForSites("Query", agent),
                                                                        Flock("Flock", agent)])

    # actual root
    root = py_trees.composites.Selector("Root", False, children=[rest_root, goToSite_root, flock_root, Explore("Explore", agent)])

    return py_trees.trees.BehaviourTree(root=root)
    
# FIXME: neither of the subtrees are working
def build_bt_2(agent):
    graze_pre = py_trees.composites.Sequence("Graze_Pre", False, [IsHungry("IsHungry", agent),
                                                                 AtSite("AtSite", agent)])
    graze_post = py_trees.composites.Selector("Graze_Post", False, [IsSatisfied("IsSatisfied", agent),
                                                                    IsBored("IsBored_Graze", agent)])
    graze_root = py_trees.composites.Selector("Graze", False, [py_trees.composites.Sequence("Graze_Sub", False, [graze_pre, Graze("Grazing", agent)])])
    
    flock_pre = py_trees.composites.Sequence("Flock_Pre", False, [HaveGroupNeighbors("GroupNeighbors_Flock", agent),
                                                                  Flock("Flocking", agent)])
    flock_post = py_trees.composites.Selector("Flock_Post", False, [SiteSelected("SiteSelected_Flock", agent),
                                                                    IsBored("IsBored_Flock", agent)])
    flock_root = py_trees.composites.Selector("Flock", False, [flock_post, flock_pre])
    
    root = py_trees.composites.Selector("Root", False, [graze_root, Explore("Explore", agent)])
    
    return py_trees.trees.BehaviourTree(root=root)

def build_ppa_bt(agent):
    rest_pa = py_trees.composites.Sequence("Rest_PA", False, [HaveGroupNeighbors("Group", agent),
                                                              AtSite("AtSite", agent),
                                                              Graze("Rest", agent)])
    # invert HaveTime?
    rest_root = py_trees.composites.Selector("Rest_Root", False, [IsBored("Timer", agent), rest_pa])

    goToSite_pa = py_trees.composites.Sequence("GoToSite_PA", False, [HaveNeighbors("Neighbors", agent),
                                                                      SiteSelected("SiteSelected_gts", agent),
                                                                      GoToSite("GoToSite", agent),
                                                                      Flock("Flock_ToSite", agent)])
    goToSite_root = py_trees.composites.Selector("GoToSite", False, [AtSite("AtSite", agent), goToSite_pa])

    explore_pa = py_trees.composites.Sequence("Explore_Actions", False, [QueryForSites("Query", agent),
                                                                        Flock("Flock_Explore", agent)])
    # explore_root = py_trees.composites.Selector("Explore", False, [SiteSelected("SiteSelected", agent), explore_pa])
    
    root = py_trees.composites.Selector("Root", False, [rest_root,
                                                        goToSite_root,
                                                        explore_pa,
                                                        Flock("Failsafe", agent)])
    
    return py_trees.trees.BehaviourTree(root=root)

if __name__ == "main":    
    # USED FOR DEBUGGING
    demo_site = Site([5, 5], 1, 10, 10)
    basic_agent = Agent(0, [0,0], 1.0, 0.0, 50, object())
    at_site_agent = Agent(1, [5, 5], 1.0, 0.0, 50, object(), site=demo_site)
    site_selected_agent = Agent(2, [0, 0], 1.0, 0.0, 50, object(), site=demo_site)
    has_neighbor_agent = Agent(3, [0, 0], 1.0, 0.0, 0.0, object(), neighbors=[1, 2], group_neighbors=None)
    has_group_neighbor_agent = Agent(4, [0, 0], 1.0, 0.0, 0.0, object(), neighbors=[0, 1, 2], group_neighbors=[0])

    test_behavior_fail = HaveGroupNeighbors("TEST_FAIL", has_neighbor_agent)
    test_behavior_success = HaveGroupNeighbors("TEST_SUCCESS", has_group_neighbor_agent)

    test_success1 = HaveNeighbors("TEST_SUCCESS1", has_neighbor_agent)
    test_success2 = HaveNeighbors("TEST_SUCCESS2", has_group_neighbor_agent)

    print(test_behavior_fail.update())
    print(test_behavior_success.update())

    print(test_success1.update())
    print(test_success2.update())
