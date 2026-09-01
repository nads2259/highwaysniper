from agent_kernel.lifecycle import Lifecycle, assert_transition


def checkpoint_after(current: Lifecycle, nxt: Lifecycle) -> Lifecycle:
    assert_transition(current, nxt)
    return nxt
