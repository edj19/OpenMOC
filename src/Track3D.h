/**
 * @file Track3D.h
 * @brief The 3D Track class.
 * @date May 9, 2015
 * @author Samuel Shaner, MIT Course, 22 (shaner@mit.edu)
 */

#ifndef TRACK3D_H_
#define TRACK3D_H_

#ifdef __cplusplus
#include "Python.h"
#include "Point.h"
#include "Material.h"
#include "Track.h"
#include "Track2D.h"
#include "LocalCoords.h"
#include <vector>
#endif



/** Forward declaration of ExtrudedFSR struct */
struct ExtrudedFSR;


/**
 * @class Track3D Track3D.h "src/Track3D.h"
 * @brief A 3D Track represents a characteristic line across the geometry.
 * @details A 3D Track has particular starting and ending points on the
 *          boundaries of the geometry and an azimuthal and polar angle.
 */
class Track3D : public Track {

protected:

  /** The polar angle for the Track */
  double _theta;

  /* Indices that are used to locate the track in the various track arrays */
  int _polar_index;
  int _z_index;
  int _lz_index;
  int _cycle_index;
  int _cycle_track_index;
  int _train_index;
  
public:
  Track3D();
  virtual ~Track3D();

  /* Setters */
  void setValues(const double start_x, const double start_y,
                 const double start_z, const double end_x,
                 const double end_y, const double end_z,
                 const double phi, const double theta);
  void setTheta(const double theta);
  void setCoords(double x0, double y0, double z0, double x1, double y1,
                 double z1);
  void setPolarIndex(int index);
  void setZIndex(int index);
  void setLZIndex(int index);
  void setCycleIndex(int index);
  void setCycleTrackIndex(int index);
  void setTrainIndex(int index);
  void setCycleFwd(bool fwd);
  
  /* Getters */
  double getTheta() const;
  int getPolarIndex();
  int getZIndex();
  int getLZIndex();
  int getCycleIndex();
  int getCycleTrackIndex();
  int getTrainIndex();
  bool getCycleFwd();
  
  std::string toString();
};



/**
 * @struct ExtrudedTrack
 * @brief An ExtrudedTrack struct represents a 2D track over the superposition
 *        plane for on-the-fly axial ray tracing. The ExtrudedTrack is split
 *        into segments for each ExtrudedFSR region that is traversed. It
 *        contains indexes and a pointer to the associated 2D Track.
 */
struct ExtrudedTrack {

  /** The lengths of the associated 2D segments (cm) */
  std::vector<FP_PRECISION> _lengths;

  /** Vector of extruded FSR region pointers associated with the 2D segments */
  std::vector<ExtrudedFSR*> _regions;

  /** The number of 2D segments associated with the extruded track */
  size_t _num_segments;

  /** Azimuthal index of the 2D and 3D tracks */
  int _azim_index;

  /** 2D track index of the 2D and 3D tracks */
  int _track_index;
  
  /** Pointer to associated 2D track */
  Track2D* _track_2D;
};


#endif /* TRACK3D_H_ */
