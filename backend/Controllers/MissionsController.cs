using Backend.Localization;
using Backend.Models;
using Backend.Services;
using Microsoft.AspNetCore.Mvc;

namespace Backend.Controllers;

[ApiController]
[Route("api/missions")]
public class MissionsController(DataStore store) : ControllerBase
{
    [HttpGet]
    public IEnumerable<MissionSummary> List(Destination? destination)
    {
        var lang = Lang.Current;
        return store.Probes
            .Where(p => destination is null || p.Destination == destination)
            .GroupBy(p => p.Mission.Get(Lang.Default))
            .Select(g =>
            {
                // the earliest event of the mission defines the date shown in the timeline
                var first = g.OrderBy(p => p.Date).First();
                return new MissionSummary(
                    first.Mission.Get(lang),
                    first.Destination,
                    first.Date,
                    first.DateKind,
                    g.Any(p => p.Status == ProbeStatus.Active) ? ProbeStatus.Active : ProbeStatus.Inactive,
                    g.Select(p => new ProbeRef(p.Id, p.Name.Get(lang), p.ImageUrl)).ToList());
            })
            .OrderBy(m => m.Date);
    }

    [HttpGet("environments")]
    public IEnumerable<object> Environments() =>
        [PlanetaryEnvironment.Moon.ToDto(Lang.Current), PlanetaryEnvironment.Mars.ToDto(Lang.Current)];
}

public record MissionSummary(string Name, Destination Destination, string Date, DateKind DateKind, ProbeStatus Status, List<ProbeRef> Probes);
public record ProbeRef(string Id, string Name, string? ImageUrl);
