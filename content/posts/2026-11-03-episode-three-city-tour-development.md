---
title: Getting the city tour moving
date: 2026-11-03
summary: Episode 3 follows Lysander around Mistral, with a visit to Granny, snowball tennis, and a few very awkward gravestones.
update_id: episode-three-city-tour-development
screenshots: content/screenshots/2026-11-03-episode-three-city-tour-development.json
---
Episode 3 starts upstairs at the Elysium. Peculier stays behind to rest, and Lysander offers to show the party around Mistral. Honeydew still demands bacon from Granny, stays behind to enjoy her company, and eventually rejoins the tour. Xephos and Honeydew try playing tennis with wooden shovels and snowballs. Jasper wants the visitors gone. The cemetery raises questions that a pleasant city tour probably should not raise.

Mejlock joins those scenes without taking over either companion’s part. Required conversations begin when you approach and interact with the right character. The choices sit above the hotbar; the main story dialogue keeps its larger panel. I checked the invitation in the actual client: clicking another NPC leaves the story waiting, choosing “Not yet” holds the scene, and accepting starts the tour. Pausing also stops the story clock.

Walking through the populated town exposed problems the script tests could not. Companions crowded Granny’s counter, a route stopped directly on a sign, and a character who had reached his mark wandered back into another companion’s way. The routes now avoid those signs, continue through doorways, and leave arrived characters looking around without wandering into the arrival path. When someone blocks a route, companions look for a clear way around them. These tests ran with teleport recovery disabled.

The native test reached the end of the episode, with player travel and most choices automated. Selected conversations were also tested through the real client. There are now 146 passing script checks. Restart testing found a separate NPC-loading bug: the terrain could be ready before its saved characters, which could create a replacement too early. The controller now waits for the saved entities before attempting recovery. The stopped-world audit passed 54 checks covering character identities, inventory, optional quest records and story completion. The Episode 3 source and test save now have a verified recovery checkpoint.

The cemetery test also caught companions entering the temple’s existing waterfalls. Ordinary routes now avoid water, and a companion pushed into it can swim out toward a checked landing area. Both the high waterfall and shallow runoff cases were recovered from their stalled saves without teleporting the characters or advancing the story by hand.

This is a private development build. Episodes 4–7 are next, in order, and the owner’s existing save and installed build are preserved. Owner playtesting is still required. The client checks also reproduced an existing intermittent startup rendering problem that appears with the preserved earlier build as well; some launches lose light-map or atlas textures, while subsequent launches render correctly. That remains an open issue before the new owner build is ready.
