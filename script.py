import pandas as pd 
import numpy as np 
import seaborn 

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

from nba_api.stats.endpoints import CommonAllPlayers
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import PlayerCareerStats

from nba_api.stats.static import teams 
from nba_api.stats.static import players 

def GatherAllPlayerInfo(): 
    
    playersInfoDict = {} 
    allPlayers = CommonAllPlayers() 
    allPlayersInfoDict = allPlayers.get_dict()
        
    k = len(allPlayersInfoDict['resultSets'][0]['rowSet'])

    for i in range(k): 
        try:
            allPlayersInfo = allPlayersInfoDict['resultSets'][0]['rowSet'][i]
            
            allPlayersInfo_TeamID = allPlayersInfo[8]
            allPlayersInfo_PlayerID = allPlayersInfo[0]

            playersInfoDict[allPlayersInfo_PlayerID] = allPlayersInfo_TeamID
        except (UnicodeEncodeError or TypeError):
            continue 

    return playersInfoDict

playerDictionary = GatherAllPlayerInfo()     

class Player: 
    
    def __init__(self,name,playerID,teamID):
        
        self.name = name 
        self.playerID = playerID
        self.teamID = teamID
        
    def retrieveShotCoordinates(self,seasonDate):
        
     shot_data = shotchartdetail.ShotChartDetail(
     team_id=self.teamID,  
     player_id=self.playerID,
     context_measure_simple='FGA',
     season_nullable=seasonDate,
     season_type_all_star='Regular Season')
        
     shots_df = shot_data.get_normalized_dict()['Shot_Chart_Detail']
          
     MadeShotsLst = []
     MissedShotsLst = [] 
               
     for i in range(len(shots_df)):
         
        if shots_df[i]['EVENT_TYPE'] == 'Made Shot':
         xCoord_madeShot = shots_df[i]['LOC_X']
         yCoord_madeShot = shots_df[i]['LOC_Y']
         MadeShotsLst.append([xCoord_madeShot,yCoord_madeShot])
         
        elif shots_df[i]['EVENT_TYPE'] == 'Missed Shot':
            xCoord_missedShot = shots_df[i]['LOC_X']
            yCoord_missedShot = shots_df[i]['LOC_Y']
            MissedShotsLst.append([xCoord_missedShot,yCoord_missedShot])
            
        
     MadeShotsDF = pd.DataFrame(MadeShotsLst, columns=['LOC_X', 'LOC_Y'])
     MissedShotsDF = pd.DataFrame(MissedShotsLst, columns=['LOC_X', 'LOC_Y'])        
     return (MadeShotsDF,MissedShotsDF)
    
    def retrieveMetricsInfo(self):
        
        PlayerStats = PlayerCareerStats(player_id=self.playerID)
        PlayerStatsInfo = PlayerStats.career_totals_regular_season.get_data_frame()
        print(PlayerStatsInfo.columns)
        
        PlayerFieldGoal = PlayerStatsInfo['FGM']
        PlayerThreePoint = PlayerStatsInfo['FG3M']
        PlayerFieldGoalAttempts = PlayerStatsInfo['FGA']
        PlayerPoints = PlayerStatsInfo['PTS']
        PlayerFreeThrowAttempts = PlayerStatsInfo['FTA']
        PlayerFreeThrow = PlayerStatsInfo['FTM']
        PlayerAssists = PlayerStatsInfo['AST']
        PlayerTurnovers = PlayerStatsInfo['TOV']
        
        EffectiveFieldGoalPercentage = (PlayerFieldGoal + ( .5 * PlayerThreePoint)) / PlayerFieldGoalAttempts
        TrueShootingPercentage = PlayerPoints / ( 2 * ( PlayerFieldGoalAttempts + .475 * PlayerFreeThrowAttempts))
        FreeThrowRate = PlayerFreeThrow / PlayerFieldGoalAttempts
        HollingerAssistRatio = PlayerAssists / ( PlayerFieldGoalAttempts + ( .475 * PlayerFreeThrowAttempts) + PlayerAssists + PlayerTurnovers )
        TurnoverPercentage = PlayerTurnovers / ( PlayerFieldGoalAttempts + ( .475*PlayerFreeThrowAttempts) + PlayerAssists + PlayerTurnovers)
        
        return (EffectiveFieldGoalPercentage,TrueShootingPercentage,FreeThrowRate,HollingerAssistRatio,TurnoverPercentage)

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

def generateShotGraph(PlayerName,MadeDF,MissedDF):
    
    MadeDF["result"] = 1   
    MissedDF["result"] = 0 
    
    TotalShotsDF = pd.concat([MadeDF, MissedDF], ignore_index=True)
    
    x_coords = list()
    y_coords = list()
    
    for i in range(-250, 250, 5):
        for j in range(-48, 423, 5):
         x_coords.append(i)
         y_coords.append(j)

    shots_hex = plt.hexbin(
        TotalShotsDF['LOC_X'], TotalShotsDF['LOC_Y'],
        extent=(-250, 250, -47.5, 422.5), cmap='Greens', gridsize=40)
    plt.close()
    
    makes_df = MadeDF
    makes_hex = plt.hexbin(
        makes_df['LOC_X'], makes_df['LOC_Y'],
        extent=(-250, 250, -47.5, 422.5), cmap=plt.cm.Reds, gridsize=40)
    
    shots_by_hex = shots_hex.get_array()
    freq_by_hex = shots_by_hex / sum(shots_by_hex)
    sizes = freq_by_hex / max(freq_by_hex) * 120
    plt.close()
    
    pcts_by_hex = makes_hex.get_array() / shots_hex.get_array()
    pcts_by_hex[np.isnan(pcts_by_hex)] = 0 

    sample_sizes = shots_hex.get_array()
    filter_threshold = 2
    
    for i in range(len(pcts_by_hex)):
        
        if sample_sizes[i] < filter_threshold:
            pcts_by_hex[i] = 0
            
    x = [i[0] for i in shots_hex.get_offsets()]
    y = [i[1] for i in shots_hex.get_offsets()]
    z = pcts_by_hex * 100

    plt.figure(figsize=(5, 4.7))
    plt.ylim(-47.5, 422.5)
    plt.xlim(-250, 250)
    FinalChart = plt.scatter(x, y, c=z, s=sizes,cmap='Greens', marker='h')
    
    draw_court(outer_lines=True)
    
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    
    sizes = freq_by_hex
    sizes = sizes / max(sizes) * 40
    max_freq = max(freq_by_hex)
    max_size = max(sizes)
    legend1 = plt.legend(
        *FinalChart.legend_elements(num=6, fmt="{x:.0f}%"),
        loc="upper right", title='Shot\nacc', fontsize='small')
    legend2 = plt.legend(
        *FinalChart.legend_elements(
            'sizes', num=6, alpha=0.8, fmt="{x:.1f}%"
            , func=lambda s: s / max_size * max_freq * 100
        ),
        loc='upper left', title='Freq (%)', fontsize='small')
    plt.gca().add_artist(legend1)
    
    plt.title=(f"{PlayerName} Shot Chart")
    
    plt.show()

def renderGraph(PlayerName,Season): 
    PlayerID = players.find_players_by_full_name(PlayerName)[0]['id']
    PlayerTeamID = playerDictionary[PlayerID]
    SelectedPlayer = Player(PlayerName,PlayerID,PlayerTeamID)
    PlayerMadeShots,PlayerMissedShots = SelectedPlayer.retrieveShotCoordinates(Season)
    generateShotGraph(PlayerName,PlayerMadeShots,PlayerMissedShots)

def renderStats(PlayerName):
    try:
        PlayerID = players.find_players_by_full_name(PlayerName)[0]['id']
        PlayerTeamID = playerDictionary[PlayerID]
        SelectedPlayer = Player(PlayerName,PlayerID,PlayerTeamID)
        EFGPerc,TrueShootingPerc,FreeThrowRate,HollingerAstRatio,TurnoverPerc = SelectedPlayer.retrieveMetricsInfo()
        
        return ( (f"{round(EFGPerc[0],3)}%"), (f"{round(TrueShootingPerc[0],3)}%"),
                (f"{round(FreeThrowRate[0],3)}%"), (f"{round(HollingerAstRatio[0],3)}%"),
                (f"{round(TurnoverPerc[0],3)}%") )
    except(IndexError):
        pass
